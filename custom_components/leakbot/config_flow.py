"""Adds config flow for Leakbot."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .api import (
    LeakbotApiClient,
    LeakbotApiClientAuthenticationError,
    LeakbotApiClientCommunicationError,
    LeakbotApiClientError,
)
from .const import DOMAIN, LOGGER


class LeakbotFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Leakbot."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.FlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            result = await self._test_credentials(
                username=user_input[CONF_USERNAME],
                password=user_input[CONF_PASSWORD],
            )

            if "token" in result:
                return self.async_create_entry(
                    title=user_input[CONF_USERNAME],
                    data=user_input,
                )
            else:
                _errors = result

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_USERNAME,
                        default=(user_input or {}).get(CONF_USERNAME),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT
                        ),
                    ),
                    vol.Required(CONF_PASSWORD): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.PASSWORD
                        ),
                    ),
                }
            ),
            errors=_errors,
        )

    async def async_step_reauth_confirm(
        self,
        user_input: dict | None = None,  # pylint: disable=unused-argument
    ) -> config_entries.FlowResult:
        """Handle reauth confirmation."""
        assert self.reauth_entry is not None

        # if there is no user input then re-direct the user step.
        _errors = {}
        if user_input is not None:
            entry_data = self.reauth_entry.data

            result = await self._test_credentials(
                username=entry_data[CONF_USERNAME],
                password=user_input[CONF_PASSWORD],
            )

            if "token" in result:
                self.hass.config_entries.async_update_entry(
                    self.reauth_entry, data={**entry_data, **user_input}
                )
                await self.hass.config_entries.async_reload(self.reauth_entry.entry_id)
                return self.async_abort(reason="reauth_successful")
            else:
                _errors = result

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_PASSWORD): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.PASSWORD
                        ),
                    ),
                }
            ),
            errors=_errors,
        )

    async def async_step_reauth(
        self, user_input: dict | None = None  # pylint: disable=unused-argument
    ) -> config_entries.FlowResult:
        """Handle configuration by re-auth."""
        self.reauth_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )
        return await self.async_step_reauth_confirm()

    async def _test_credentials(self, username: str, password: str) -> str:
        """Validate credentials."""
        client = LeakbotApiClient(
            username=username,
            password=password,
            session=async_create_clientsession(self.hass),
        )

        result = {}
        try:
            result = await client.login()
        except LeakbotApiClientAuthenticationError as exception:
            LOGGER.warning(exception)
            result["base"] = "auth"
        except LeakbotApiClientCommunicationError as exception:
            LOGGER.error(exception)
            result["base"] = "connection"
        except LeakbotApiClientError as exception:
            LOGGER.exception(exception)
            result["base"] = "unknown"

        return result
