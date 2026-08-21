"""Leakbot Calendar Tests."""

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
        [Platform.CALENDAR],
    ):
        yield


async def test_calendar_setup(
    hass: HomeAssistant,
    leakbot_api: Application,
    aiohttp_client: ClientSessionGenerator,
):
    """Test Calendar are Created and Updated."""
    session = await aiohttp_client(leakbot_api)
    entry = MockConfigEntry(domain=DOMAIN, data=VALID_LOGIN)
    entry.add_to_hass(hass)

    with patch(
        "custom_components.leakbot.async_get_clientsession",
        return_value=session,
    ):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    # Check we called the Mock and we have a Calendar.
    assert hass.states.async_entity_ids_count(Platform.CALENDAR) > 0, (
        "Calendar Failed to Create"
    )

    assert hass.states.get("calendar.leakbot_5abcdef_events") is not None
