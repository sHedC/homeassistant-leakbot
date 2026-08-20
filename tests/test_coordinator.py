"""Test the Leakbot Data Update coordinator."""

from aiohttp import ClientSession

from ical.calendar import Calendar

from homeassistant.core import HomeAssistant

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.leakbot.api import LeakbotApiClient
from custom_components.leakbot.const import DOMAIN
from custom_components.leakbot.coordinator import LeakbotDataUpdateCoordinator

from .conftest import VALID_LOGIN


async def test_coordinator_setup(
    hass: HomeAssistant,
    leakbot_api_client: LeakbotApiClient,
):
    """Test the Coordinator sets up."""
    entry = MockConfigEntry(domain=DOMAIN, data=VALID_LOGIN)
    coordinator = LeakbotDataUpdateCoordinator(hass, leakbot_api_client, entry, 15)
    assert coordinator


async def test_coordinator_data(
    hass: HomeAssistant,
    leakbot_api_client: LeakbotApiClient,
):
    """Test the Data Update works."""
    entry = MockConfigEntry(domain=DOMAIN, data=VALID_LOGIN)
    assert leakbot_api_client.is_connected

    coordinator = LeakbotDataUpdateCoordinator(hass, leakbot_api_client, entry, 15)
    await coordinator.async_refresh()

    assert coordinator.is_connected
    assert coordinator.data
    assert "123456" in coordinator.data["devices"]

    device = coordinator.data["devices"]["123456"]
    assert device["last_update"]["messageTimestamp"] == "2025-04-11 02:16:26"
    assert device["water_usage"]["days"][0]["dayNumber"] == "6"

    device_cal: Calendar = device["calendar"]
    assert device_cal.events[0].summary == "HighFlow"


async def test_auth_error(
    hass: HomeAssistant,
    leakbot_session: ClientSession,
):
    """Test the Data Update works."""
    # This test requires teh config entry to be set up
    # properly to avoid Assert Exception in Teardown
    entry = MockConfigEntry(domain=DOMAIN, data=VALID_LOGIN)
    entry.add_to_hass(hass)

    api = LeakbotApiClient("wrong", "creds", leakbot_session)
    coordinator = LeakbotDataUpdateCoordinator(hass, api, entry, 15)
    await coordinator.async_refresh()
    assert not coordinator.is_connected

    # Lef the flow finish.
    await hass.async_block_till_done()


async def test_token_error(
    hass: HomeAssistant,
    leakbot_api_client: LeakbotApiClient,
):
    """Test the Data Update works."""
    entry = MockConfigEntry(domain=DOMAIN, data=VALID_LOGIN)
    result = await leakbot_api_client.login()

    assert leakbot_api_client.is_connected
    assert result["token"]
    assert result["tenant_id"]

    coordinator = LeakbotDataUpdateCoordinator(hass, leakbot_api_client, entry, 15)
    await coordinator.async_refresh()
    assert coordinator.data

    # Token Invalid but refreshes.
    leakbot_api_client._token = "INVALID"

    await coordinator.async_refresh()
    await hass.async_block_till_done()
    assert coordinator.data
    assert leakbot_api_client._token != "INVALID"
