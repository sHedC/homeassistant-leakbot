"""Leakbot Sensor Tests."""

from datetime import datetime
from unittest.mock import patch
import pytest

from aiohttp.web import Application

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

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

    with patch(
        "custom_components.leakbot.async_get_clientsession",
        return_value=session,
    ):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    # Check we called the Mock and we have a Sensor.
    assert hass.states.async_entity_ids_count(Platform.SENSOR) > 0, (
        "Sensors Failed to Create"
    )

    state = hass.states.get("sensor.leakbot_5abcdef_device_status")
    assert state is not None
    assert state.state == "leak_inactive"

    state = hass.states.get("sensor.leakbot_5abcdef_messageTimestamp")
    assert state is not None
    assert state.state == "2025-04-11T02:16:26+00:00"


async def test_leak_free_days_found(
    hass: HomeAssistant,
    leakbot_api: Application,
    aiohttp_client: ClientSessionGenerator,
):
    """Test Sensor for Leak Free Days."""
    session = await aiohttp_client(leakbot_api)
    entry = MockConfigEntry(domain=DOMAIN, data=VALID_LOGIN)
    entry.add_to_hass(hass)

    with patch(
        "custom_components.leakbot.async_get_clientsession",
        return_value=session,
    ):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    # Check we called the Mock and we have a Sensor.
    assert hass.states.async_entity_ids_count(Platform.SENSOR) > 0, (
        "Sensors Failed to Create"
    )

    # Check Leak Free Days Status on good data.
    state = hass.states.get("sensor.leakbot_5abcdef_leak_free_days")
    assert state is not None
    assert state.state == "722"


async def test_leak_free_days_missing(
    hass: HomeAssistant,
    leakbot_api: Application,
    aiohttp_client: ClientSessionGenerator,
):
    """Test Sensor for Leak Free Days where data is missing."""
    """Test Sensor for Leak Free Days."""
    session = await aiohttp_client(leakbot_api)
    entry = MockConfigEntry(domain=DOMAIN, data=VALID_LOGIN)
    entry.add_to_hass(hass)

    with patch(
        "custom_components.leakbot.async_get_clientsession",
        return_value=session,
    ):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    # Check we called the Mock and we have a Sensor.
    assert hass.states.async_entity_ids_count(Platform.SENSOR) > 0, (
        "Sensors Failed to Create"
    )

    # Check Leak Free days on good and bad data.
    state = hass.states.get("sensor.leakbot_5abcdeg_leak_free_days")
    assert state is not None

    no_days = (
        datetime.now().date()
        - datetime.strptime("2022-02-16 16:39:23", "%Y-%m-%d %H:%M:%S").date()
    ).days - 1
    assert state.state == str(no_days)
