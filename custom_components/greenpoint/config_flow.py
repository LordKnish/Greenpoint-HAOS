"""Config flow for Greenpoint IGH Compact integration."""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_TOKEN
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .api import CannotConnect, GreenpointApiClient, InvalidAuth
from .const import DEFAULT_PORT, DOMAIN

_LOGGER = logging.getLogger(__name__)

class GreenpointConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Greenpoint IGH Compact."""

    VERSION = 1

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                # Create API client
                client = GreenpointApiClient(
                    host=user_input[CONF_HOST],
                    port=user_input.get(CONF_PORT, DEFAULT_PORT),
                    token=user_input[CONF_TOKEN],
                    session=self.hass.helpers.aiohttp_client.async_get_clientsession(),
                )

                # Test connection
                if not await client.test_connection():
                    raise CannotConnect()

                # Check if scenarios are set up
                scenarios = await client.get_scenarios()
                if not scenarios:
                    return await self.async_step_scenario_setup(user_input)

                # Create entry
                return self.async_create_entry(
                    title=f"IGH Compact ({user_input[CONF_HOST]})",
                    data=user_input,
                )

            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
                    vol.Required(CONF_TOKEN): str,
                }
            ),
            errors=errors,
        )

    async def async_step_scenario_setup(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle the scenario setup step."""
        errors = {}

        if user_input is not None:
            if user_input.get("confirm_setup"):
                # Create entry
                return self.async_create_entry(
                    title=f"IGH Compact ({user_input[CONF_HOST]})",
                    data=user_input,
                )
            else:
                errors["base"] = "scenarios_not_setup"

        return self.async_show_form(
            step_id="scenario_setup",
            data_schema=vol.Schema(
                {
                    vol.Required("confirm_setup"): bool,
                }
            ),
            description_placeholders={
                "scenario_setup_url": "https://github.com/your-repo/greenpoint-haos/wiki/Scenario-Setup",
            },
            errors=errors,
        )

    async def async_step_import(self, import_info):
        """Handle import from configuration.yaml."""
        return await self.async_step_user(import_info)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for the integration."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options = {
            vol.Optional(
                "scan_interval",
                default=self.config_entry.options.get("scan_interval", 30),
            ): int,
        }

        return self.async_show_form(step_id="init", data_schema=vol.Schema(options))
