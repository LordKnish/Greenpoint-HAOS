"""Config flow for Greenpoint IGH Compact integration."""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional, List

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_TOKEN
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import CannotConnect, GreenpointApiClient, InvalidAuth
from .const import DEFAULT_PORT, DOMAIN

_LOGGER = logging.getLogger(__name__)

class GreenpointConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Greenpoint IGH Compact."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._units: List[Dict[str, Any]] = []
        self._config_data: Dict[str, Any] = {}

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                # Store config data for later use
                self._config_data = user_input.copy()

                # Create API client
                client = GreenpointApiClient(
                    host=user_input[CONF_HOST],
                    port=user_input.get(CONF_PORT, DEFAULT_PORT),
                    token=user_input[CONF_TOKEN],
                    session=async_get_clientsession(self.hass),
                )

                # Test connection
                if not await client.test_connection():
                    raise CannotConnect()

                # Get units to check what scenarios need to be created
                self._units = await client.get_unit_list()
                if not self._units:
                    errors["base"] = "no_units"
                else:
                    # Show scenario setup instructions
                    return await self.async_step_scenario_setup()

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

    async def async_step_scenario_setup(self) -> FlowResult:
        """Handle the scenario setup step."""
        errors = {}

        if self.hass.data.get(DOMAIN, {}).get("user_input"):
            user_input = self.hass.data[DOMAIN]["user_input"]
            if user_input.get("confirm_setup"):
                # Create entry using stored config data
                return self.async_create_entry(
                    title=f"IGH Compact ({self._config_data[CONF_HOST]})",
                    data=self._config_data,
                )
            else:
                errors["base"] = "scenarios_not_setup"

        # Create list of required scenarios
        required_scenarios = []
        for unit in self._units:
            unit_name = unit.get("name", "Unknown")
            required_scenarios.extend([
                f"{unit_name} On",
                f"{unit_name} Off"
            ])

        return self.async_show_form(
            step_id="scenario_setup",
            data_schema=vol.Schema(
                {
                    vol.Required("confirm_setup"): bool,
                }
            ),
            description_placeholders={
                "scenario_list": "\n".join(f"- {scenario}" for scenario in required_scenarios),
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
