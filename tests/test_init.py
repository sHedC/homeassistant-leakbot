"""Test leakbot setup process."""

import pytest

from unittest.mock import patch

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntryState

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.leakbot import (
    async_setup_entry,
    async_reload_entry,
    LeakbotDataUpdateCoordinator,
)
from custom_components.leakbot.const import DOMAIN

from .conftest import VALID_LOGIN


@pytest.fixture
def mock_entitydata() -> dict[str, any]:
    """Mock data for the API."""
    return {"devices": {"123456": {"id": "123456", "device_status": "Leak Inactive"}}}


@pytest.mark.parametrize("expected_lingering_timers", [True])
async def test_setup_unload_and_reload_entry(
    hass: HomeAssistant, mock_entitydata: dict
):
    """Test a Configured Instance that Logs In and Updates."""
    entry = MockConfigEntry(domain=DOMAIN, data=VALID_LOGIN)
    entry.add_to_hass(hass)

    with patch(
        (
            "custom_components.leakbot.coordinator."
            "LeakbotDataUpdateCoordinator._async_update_data"
        ),
        return_value=mock_entitydata,
    ) as mock_sync:
        assert await async_setup_entry(hass, entry)
        await hass.async_block_till_done()

        assert (
            len(hass.config_entries.flow.async_progress()) == 0
        ), "Flow is in Progress it should not be."

        assert DOMAIN in hass.data and entry.entry_id in hass.data[DOMAIN]
        assert isinstance(
            hass.data[DOMAIN][entry.entry_id], LeakbotDataUpdateCoordinator
        )

        # Reload the entry and assert that the data from above is still there
        assert await async_reload_entry(hass, entry) is None
        assert DOMAIN in hass.data and entry.entry_id in hass.data[DOMAIN]
        assert isinstance(
            hass.data[DOMAIN][entry.entry_id], LeakbotDataUpdateCoordinator
        )

    assert len(mock_sync.mock_calls) > 0


async def test_unload_entry(hass: HomeAssistant, mock_entitydata: dict):
    """Test being able to unload an entry."""
    entry = MockConfigEntry(domain=DOMAIN, data=VALID_LOGIN, entry_id="test")
    entry.add_to_hass(hass)

    # Check the Config is initiated
    with patch(
        (
            "custom_components.leakbot.coordinator."
            "LeakbotDataUpdateCoordinator._async_update_data"
        ),
        return_value=mock_entitydata,
    ) as mock_updater:
        assert (
            await hass.config_entries.async_setup(entry.entry_id) is True
        ), "Component did not setup correctly."
        await hass.async_block_till_done()

    assert len(mock_updater.mock_calls) >= 1, "Mock Entity was not called."

    # Perform and Check Unload Config
    assert (
        await hass.config_entries.async_unload(entry.entry_id) is True
    ), "Component Config Unload Failed."
    assert entry.state == ConfigEntryState.NOT_LOADED
