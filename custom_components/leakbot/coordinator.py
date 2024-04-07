"""DataUpdateCoordinator for Leakbot."""

from __future__ import annotations

from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.exceptions import ConfigEntryAuthFailed

from .api import (
    LeakbotApiClient,
    LeakbotApiClientAuthenticationError,
    LeakbotApiClientError,
)
from .const import DOMAIN, LOGGER


class LeakbotDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: LeakbotApiClient,
        entry_id: str,
    ) -> None:
        """Initialize."""
        self.client = client
        self.entry_id = entry_id

        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=60),
        )

    def remove_old_entities(self, platform: str) -> None:
        """Remove obsolete entities."""

    async def _async_update_data(self):
        """Update data via library."""
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

            # Water Usage
            return result_data
        except LeakbotApiClientAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except LeakbotApiClientError as exception:
            raise UpdateFailed(exception) from exception
