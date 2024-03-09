"""DataUpdateCoordinator for Leakbot."""

from __future__ import annotations

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
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
            update_interval=timedelta(minutes=5),
        )

    async def _async_update_data(self):
        """Update data via library."""
        try:
            return await self.client.async_get_data()
        except LeakbotApiClientAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except LeakbotApiClientError as exception:
            raise UpdateFailed(exception) from exception
