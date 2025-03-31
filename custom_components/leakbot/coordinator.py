"""DataUpdateCoordinator for Leakbot."""
from __future__ import annotations

import logging

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.entity_registry import (
    async_get,
    async_entries_for_config_entry,
)

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

                _LOGGER.debug("Water Usage: %s", device["water_usage"])
            return result_data
        except LeakbotApiClientError as exception:
            raise UpdateFailed(exception) from exception
