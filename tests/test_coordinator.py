"""Test the Leakbot Data Update coordinator."""

from aiohttp.web import Application

from homeassistant.core import HomeAssistant

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.leakbot.api import LeakbotApiClient
from custom_components.leakbot.const import DOMAIN
from custom_components.leakbot.coordinator import LeakbotDataUpdateCoordinator

from .conftest import ClientSessionGenerator, VALID_LOGIN


async def test_coordinator_setup(hass: HomeAssistant):
    """Test the Coordinator sets up."""
    entry = MockConfigEntry(domain=DOMAIN, data=VALID_LOGIN)
    coordinator = LeakbotDataUpdateCoordinator(
        hass, LeakbotApiClient("", "", None), entry
    )
    assert coordinator


async def test_coordinator_data(
    hass: HomeAssistant,
    leakbot_api: Application,
    aiohttp_client: ClientSessionGenerator,
):
    """Test the Data Update works."""
    session = await aiohttp_client(leakbot_api)
    entry = MockConfigEntry(domain=DOMAIN, data=VALID_LOGIN)

    api = LeakbotApiClient(
        VALID_LOGIN["username"],
        VALID_LOGIN["password"],
        session,
    )

    assert api.is_connected

    coordinator = LeakbotDataUpdateCoordinator(hass, api, entry)
    await coordinator.async_refresh()

    assert coordinator.data
    assert "123456" in coordinator.data["devices"]


async def test_token_error(
    hass: HomeAssistant,
    leakbot_api: Application,
    aiohttp_client: ClientSessionGenerator,
):
    """Test the Data Update works."""
    session = await aiohttp_client(leakbot_api)
    entry = MockConfigEntry(domain=DOMAIN, data=VALID_LOGIN)

    api = LeakbotApiClient(
        VALID_LOGIN["username"],
        VALID_LOGIN["password"],
        session,
    )

    assert api.is_connected

    coordinator = LeakbotDataUpdateCoordinator(hass, api, entry)
    await coordinator.async_refresh()
    assert coordinator.data

    # Token Invalid but refreshes.
    api._token = "INVALID"
    await coordinator.async_refresh()
    assert coordinator.data
    assert api._token != "INVALID"
