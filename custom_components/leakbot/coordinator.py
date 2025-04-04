"""DataUpdateCoordinator for Leakbot."""
from __future__ import annotations

import logging

from datetime import date, datetime, timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.components.recorder.statistics import (
    async_add_external_statistics,
    get_last_statistics,
    statistics_during_period,
)
from homeassistant.core import HomeAssistant
from homeassistant.const import UnitOfVolume
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.entity_registry import (
    async_get,
    async_entries_for_config_entry,
)
from homeassistant.components.recorder.models import StatisticData, StatisticMetaData, StatisticMeanType
from homeassistant.util import slugify, dt


from .api import (
    LeakbotApiClient,
    LeakbotApiClientAuthenticationError,
    LeakbotApiClientCommunicationError,
    LeakbotApiClientTokenError,
    LeakbotApiClientError,
)
from .const import DOMAIN, LOGGER

_LOGGER = logging.getLogger(__name__)


class LeakbotDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: LeakbotApiClient,
        entry: ConfigEntry,
    ) -> None:
        """Initialize."""
        self.client = client
        self._entry = entry
        self._connected = False

        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=60),
        )

        self.old_entries: dict[str, list[str]] = {}
        self.entity_registry = async_get(hass)

        # Convert registries into Entity Platform and ID.
        registry_entries = async_entries_for_config_entry(
            self.entity_registry, entry.entry_id
        )
        for reg_entity in registry_entries:
            if reg_entity.domain not in self.old_entries:
                self.old_entries[reg_entity.domain] = []
            self.old_entries[reg_entity.domain].append(reg_entity.entity_id)

    @property
    def is_connected(self) -> bool:
        """Return true if connected."""
        return self._connected

    def remove_old_entities(self, platform: str) -> None:
        """Remove obsolete entities."""
        if platform in self.old_entries:
            for entity_id in self.old_entries[platform]:
                LOGGER.warning(
                    "Removing Old Entities for platform: %s, entity_id: %s",
                    platform,
                    entity_id,
                )
                self.entity_registry.async_remove(entity_id)

    async def _client_login(self) -> None:
        """Login to the API Client."""
        self._connected = False
        try:
            await self.client.login()
            self._connected = True
        except LeakbotApiClientAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except LeakbotApiClientCommunicationError as exception:
            raise UpdateFailed(exception) from exception
        except LeakbotApiClientError as exception:
            raise UpdateFailed(exception) from exception

    async def _async_update_data(self):
        """Update data via library."""
        if not self._connected:
            await self._client_login()
        else:
            try:
                # Test Token is still valid
                await self.client.get_account_myread()
            except LeakbotApiClientTokenError:
                await self._client_login()
            except LeakbotApiClientError as exception:
                raise UpdateFailed(exception) from exception

        try:
            result_data = self.data
            if result_data is None:
                # First Run.
                account = await self.client.get_account_myread()
                address = await self.client.get_address_myread()
                devices = await self.client.get_device_list()
                tenant = await self.client.get_tenant_myview()

                device_data: dict[str, any] = {}
                for device in devices.get("IDs"):
                    device_data[device["id"]] = device

                result_data = {
                    "account": account,
                    "address": address,
                    "tenant": tenant,
                    "devices": device_data,
                }

            # Update Device Information and Water Usage
            for device_id, device in result_data["devices"].items():
                device["info"] = await self.client.get_device_data(device_id)
                messages = await self.client.get_device_messages(device_id)
                device["last_update"] = messages["list"]["record"][0]

                # Water Usage
                device["water_usage"] = await self.client.get_device_water_usage(
                    device_id,
                    0
                )
                await self._insert_statistics(device)

                _LOGGER.debug("Water Usage: %s", device["water_usage"])

            return result_data
        except LeakbotApiClientError as exception:
            raise UpdateFailed(exception) from exception

    async def _insert_statistics(self, device: dict[str, any]) -> None:
        """Insert Leakbot Statistics."""
        id = f"{DOMAIN}:water_usage"

        water_metadata = StatisticMetaData(
            mean_type=StatisticMeanType.NONE,
            has_sum=True,
            name="water_usage",
            source=DOMAIN,
            statistic_id=f"{DOMAIN}:water_usage",
            unit_of_measurement=UnitOfVolume.LITERS,
        )

        # Get the current query time and step through history.
        water_usage = device["water_usage"]
        query_date = dt.as_local(datetime.fromtimestamp(water_usage["ts"] / 1000))
        query_date = query_date.replace(hour=0, minute=0, second=0, microsecond=0)

        water_sum = 0
        water_stats = []
        for day in reversed(water_usage["days"]):
            water_sum += float(day["details"]["night"])
            water_stats.append(StatisticData(
                start=query_date.replace(hour=0) + timedelta(days=int(day["offset"])),
                state=float(day["details"]["night"]),
                sum=water_sum
            ))
            water_sum += float(day["details"]["morning"])
            water_stats.append(StatisticData(
                start=query_date.replace(hour=6) + timedelta(days=int(day["offset"])),
                state=float(day["details"]["morning"]),
                sum=water_sum
            ))
            water_sum += float(day["details"]["afternoon"])
            water_stats.append(StatisticData(
                start=query_date.replace(hour=12) + timedelta(days=int(day["offset"])),
                state=float(day["details"]["afternoon"]),
                sum=water_sum
            ))
            water_sum += float(day["details"]["evening"])
            water_stats.append(StatisticData(
                start=query_date.replace(hour=18) + timedelta(days=int(day["offset"])),
                state=float(day["details"]["evening"]),
                sum=water_sum
            ))

            async_add_external_statistics(
                self.hass,
                water_metadata,
                water_stats
            )
