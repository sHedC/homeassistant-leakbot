"""Custom integration to integrate Leakbot with Home Assistant.

For more details about this integration, please refer to
https://github.com/sHedC/homeassistant-leakbot
"""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_PASSWORD,
    CONF_USERNAME,
    CONF_SCAN_INTERVAL,
    Platform,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import LeakbotApiClient
from .const import DOMAIN, DEFAULT_REFRESH
from .coordinator import LeakbotDataUpdateCoordinator

PLATFORMS: list[Platform] = [
    Platform.DEVICE_TRACKER,
    Platform.SENSOR,
    Platform.CALENDAR,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up this integration using UI."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator = LeakbotDataUpdateCoordinator(
        hass=hass,
        client=LeakbotApiClient(
            username=entry.data[CONF_USERNAME],
            password=entry.data[CONF_PASSWORD],
            session=async_get_clientsession(hass),
        ),
        entry=entry,
        scan_interval=entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_REFRESH),
    )
    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    if unloaded := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
