"""Leakbot Sensor Tests."""

from unittest.mock import patch
import pytest

from aiohttp.web import Application

from homeassistant.core import HomeAssistant
from homeassistant.const import Platform

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.leakbot.const import DOMAIN

from .conftest import ClientSessionGenerator, VALID_LOGIN


@pytest.fixture(autouse=True)
def override_entity():
    """Override the ENTITIES to test Sensors."""
    with patch(
        "custom_components.leakbot.PLATFORMS",
        [Platform.SENSOR],
    ):
        yield


async def test_sensor_setup(
    hass: HomeAssistant,
    leakbot_api: Application,
    aiohttp_client: ClientSessionGenerator,
):
    """Test Sensors are Created and Updated."""
    session = await aiohttp_client(leakbot_api)
    entry = MockConfigEntry(domain=DOMAIN, data=VALID_LOGIN)
    entry.add_to_hass(hass)

    # hass.data.setdefault(DOMAIN, {})
    # coordinator = LeakbotDataUpdateCoordinator(hass, api, entry.entry_id)
    # hass.data[DOMAIN][entry.entry_id] = coordinator

    with patch(
        "custom_components.leakbot.async_get_clientsession",
        return_value=session,
    ):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    # Check we called the Mock and we have a Sensor.
    assert (
        hass.states.async_entity_ids_count(Platform.SENSOR) > 0
    ), "Sensors Failed to Create"

    state = hass.states.get("sensor.leakbot_123456_device_status")
    assert state.state == "Leak Inactive"
    assert state.name == "Device Status"
