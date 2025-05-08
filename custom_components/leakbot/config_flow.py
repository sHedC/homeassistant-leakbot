"""Adds config flow for Leakbot."""

from __future__ import annotations

import voluptuous as vol
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    OptionsFlow,
    CONN_CLASS_CLOUD_POLL,
)
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, CONF_SCAN_INTERVAL
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .api import (
    LeakbotApiClient,
    LeakbotApiClientAuthenticationError,
    LeakbotApiClientCommunicationError,
    LeakbotApiClientError,
)
from .const import DOMAIN, LOGGER, DEFAULT_REFRESH


class LeakbotFlowHandler(ConfigFlow, domain=DOMAIN):
    """Config flow for Leakbot."""

    VERSION = 1
    CONNECTION_CLASS = CONN_CLASS_CLOUD_POLL

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> FlowResult:
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
    ) -> FlowResult:
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
        self,
        user_input: dict | None = None,  # pylint: disable=unused-argument
    ) -> FlowResult:
        """Handle configuration by re-auth."""
        self.reauth_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )
        return await self.async_step_reauth_confirm()

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> OptionsFlow:
        """Return the option flow handler."""
        return LeakbotOptionsFlowHandler(config_entry)

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


class LeakbotOptionsFlowHandler(OptionsFlow):
    """Config flow options for Leakbot."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize Leakbot options flow."""
        self.config_entry = config_entry
        self.options = dict(config_entry.options)

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> FlowResult:
        """Manage the Leakbot options."""
        if user_input is not None:
            self.options.update(user_input)
            return self.async_create_entry(
                title=self.config_entry.data.get(CONF_USERNAME), data=self.options
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_SCAN_INTERVAL,
                        default=self.options.get(CONF_SCAN_INTERVAL, DEFAULT_REFRESH),
                    ): vol.All(vol.Coerce(int), vol.Range(min=15, max=21600))
                }
            ),
        )
