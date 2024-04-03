"""Test leakbot config flow."""

from unittest.mock import patch

from homeassistant import config_entries, data_entry_flow
from homeassistant.core import HomeAssistant
from homeassistant.const import (
    CONF_PASSWORD,
    CONF_USERNAME,
    CONF_TOKEN,
)

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.leakbot.api import LeakbotApiClientAuthenticationError
from custom_components.leakbot.const import DOMAIN


async def test_form_success(hass: HomeAssistant):
    """Test setting up the form and configuring."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["errors"] == {}

    # Patch to bypass authentication and stop setup entry.
    with patch(
        "custom_components.leakbot.config_flow.LeakbotFlowHandler._test_credentials",
        return_value={"token": "tokencode"},
    ) as mock_authenticate, patch(
        "custom_components.leakbot.async_setup_entry", return_value=False
    ):
        setup_result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_PASSWORD: "hash", CONF_USERNAME: "user.name"},
        )
        await hass.async_block_till_done()

    assert setup_result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert setup_result["title"] == "user.name"

    assert len(mock_authenticate.mock_calls) == 1

    assert setup_result["data"][CONF_PASSWORD] == "hash"
    assert setup_result["data"][CONF_USERNAME] == "user.name"
    assert setup_result["data"][CONF_TOKEN] == "tokencode"


async def test_form_invalid_auth(hass: HomeAssistant):
    """Test Form Login with Invalid Authentication."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["errors"] == {}

    # Patch Test Credentials to Fail.
    with patch(
        "custom_components.leakbot.api.LeakbotApiClient.login",
        side_effect=LeakbotApiClientAuthenticationError(
            "45", "User does not exist or Username and Password combination is wrong"
        ),
    ) as mock_authenticate:
        setup_result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_PASSWORD: "hash", CONF_USERNAME: "user.name"},
        )
        await hass.async_block_till_done()

    assert setup_result["type"] == data_entry_flow.FlowResultType.FORM
    assert setup_result["errors"]["base"] == "auth"

    assert len(mock_authenticate.mock_calls) == 1


async def test_form_reauth(hass: HomeAssistant):
    """Test Form Login Re-authentication."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_PASSWORD: "hash",
            CONF_USERNAME: "user.name",
            CONF_TOKEN: "tokencode",
        },
        unique_id="111010202002020",
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={
            "source": config_entries.SOURCE_REAUTH,
            "entry_id": entry.entry_id,
        },
        data=entry.data,
    )
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["errors"] == {}

    # Patch to bypass authentication and stop setup entry.
    with patch(
        "custom_components.leakbot.config_flow.LeakbotFlowHandler._test_credentials",
        return_value={"token": "tokencode"},
    ), patch("custom_components.leakbot.async_setup_entry", return_value=False):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_PASSWORD: "hash"},
        )
        await hass.async_block_till_done()

    assert result2["type"] == "abort"
    assert result2["reason"] == "reauth_successful"
