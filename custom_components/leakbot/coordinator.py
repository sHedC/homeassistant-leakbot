"""DataUpdateCoordinator for Leakbot."""

from __future__ import annotations

import logging

from dataclasses import dataclass
from datetime import timedelta, datetime

from homeassistant.config_entries import ConfigEntry
from homeassistant.components.calendar import (
    CalendarEntity,
    CalendarEntityDescription,
    CalendarEntityFeature,
    CalendarEvent,
    CalendarListView,
)
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
                    device_id, 0
                )

                # Check for Alerts, Informational for now!!!
                messages = await self.client.get_device_messages(device_id)
                for message in messages["list"]["record"]:
                    if message["msg_type"] == "10" and message["event_type"] != "null":
                        LOGGER.warning(
                            "Unrecognized Alert, please report! Date: %s, Msg Type: %s, Event Type: %s",
                            message["messageTimestamp"],
                            message["msg_type"],
                            message["event_type"],
                        )

                    if message["msg_type"] == "9" and int(message["event_type"]) > 2:
                        LOGGER.warning(
                            "Unrecognized Alert, please report! Date: %s, Msg Type: %s, Event Type: %s",
                            message["messageTimestamp"],
                            message["msg_type"],
                            message["event_type"],
                        )

                # Look for Event Messages to add to calendar.
                # Can do events from past 90 days,
                # but better if from last successful refresh.
                start_date = datetime.now() - timedelta(days=90)
                starting_date = start_date.strftime("%Y-%m-%d %H:%M:%S")
                events = await self.client.get_device_simple_event_list(
                    device_id, starting_date
                )
                device["events"] = events["events"]

                # Temporary Logger.
                LOGGER.warning("Events: %s", device["events"])

            return result_data
        except LeakbotApiClientError as exception:
            raise UpdateFailed(exception) from exception

    async def async_get_events(
        self, device_id: str, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        """Get Calendar Events within a date range."""
        events = await self.client.get_device_simple_event_list(
            device_id, start_date.strftime("%Y-%m-%d %H:%M:%S")
        )

        calendar_events = []

        for event in events["events"]:
            event_start = datetime.fromisoformat(event["derived_event_created"])
            event_closed = event["derived_event_closed"]

            if event["derived_event_closed"] == "null":
                event_end = event_start + timedelta(minutes=30)
            else:
                event_end = datetime.fromisoformat(event_closed)

            if event_start <= event_end:
                calendar_events.append(
                    CalendarEvent(
                        start=dt.as_local(event_start),
                        end=dt.as_local(event_end),
                        summary=event["derived_event_code"],
                    )
                )

        return calendar_events
