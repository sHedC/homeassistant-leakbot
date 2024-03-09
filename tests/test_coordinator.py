"""Test the Leakbot Data Update coordinator."""

from homeassistant.core import HomeAssistant

from custom_components.leakbot.api import LeakbotApiClient
from custom_components.leakbot.coordinator import LeakbotDataUpdateCoordinator


async def test_coordinator_setup(hass: HomeAssistant):
    """Test the Coordinator sets up."""

    coordinator = LeakbotDataUpdateCoordinator(
        hass, LeakbotApiClient("", "", None), "1234"
    )
    assert coordinator
