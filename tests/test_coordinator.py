"""Test the Leakbot Data Update coordinator."""

from aiohttp.web import Application

from homeassistant.core import HomeAssistant

from custom_components.leakbot.api import LeakbotApiClient
from custom_components.leakbot.coordinator import LeakbotDataUpdateCoordinator

from .conftest import ClientSessionGenerator, VALID_LOGIN


async def test_coordinator_setup(hass: HomeAssistant):
    """Test the Coordinator sets up."""

    coordinator = LeakbotDataUpdateCoordinator(
        hass, LeakbotApiClient("", "", None), "1234"
    )
    assert coordinator


async def test_coordinator_data(
    hass: HomeAssistant,
    leakbot_api: Application,
    aiohttp_client: ClientSessionGenerator,
):
    """Test the Data Update works."""
    session = await aiohttp_client(leakbot_api)
    api = LeakbotApiClient(
        VALID_LOGIN["username"],
        VALID_LOGIN["password"],
        session,
        token=VALID_LOGIN["token"],
    )

    assert api.is_connected

    coordinator = LeakbotDataUpdateCoordinator(hass, api, "1234")
    await coordinator.async_refresh()

    assert coordinator.data
    assert "123456" in coordinator.data["devices"]
