"""Platform for Greenpoint IGH Compact light integration."""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ColorMode,
    LightEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import GreenpointDataUpdateCoordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Greenpoint IGH Compact light platform."""
    coordinator: GreenpointDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    # Add lights for each unit
    async_add_entities(
        GreenpointLight(coordinator, unit)
        for unit in coordinator.data
        if unit.get("type") == "light"
    )

class GreenpointLight(CoordinatorEntity, LightEntity):
    """Representation of a Greenpoint IGH Compact light."""

    def __init__(
        self,
        coordinator: GreenpointDataUpdateCoordinator,
        device: Dict[str, Any],
    ) -> None:
        """Initialize the light."""
        super().__init__(coordinator)
        self.device = device
        self._attr_name = device.get("name", "Unknown Light")
        self._attr_unique_id = f"{DOMAIN}_{device.get('full_id')}"
        self._attr_is_on = device.get("status", 0) == 1
        self._attr_brightness = device.get("brightness", 255)
        self._attr_color_mode = ColorMode.BRIGHTNESS
        self._attr_supported_color_modes = {ColorMode.BRIGHTNESS}

    @property
    def device_info(self) -> Dict[str, Any]:
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self.device.get("full_id"))},
            "name": self._attr_name,
            "manufacturer": "Greenpoint",
            "model": "IGH Compact",
        }

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the light on."""
        scenario_name = f"{self._attr_name} On"
        _LOGGER.debug("Attempting to turn on light %s using scenario: %s", self._attr_name, scenario_name)
        
        # Get available scenarios
        scenarios = await self.coordinator.api.get_scenarios()
        _LOGGER.debug("Available scenarios: %s", scenarios)
        
        # Try to run the scenario
        result = await self.coordinator.api.run_scenario(scenario_name)
        _LOGGER.debug("Scenario execution result: %s", result)
        
        if result:
            self._attr_is_on = True
            if ATTR_BRIGHTNESS in kwargs:
                self._attr_brightness = kwargs[ATTR_BRIGHTNESS]
            self.async_write_ha_state()
            # Schedule an immediate update
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the light off."""
        scenario_name = f"{self._attr_name} Off"
        _LOGGER.debug("Attempting to turn off light %s using scenario: %s", self._attr_name, scenario_name)
        
        # Get available scenarios
        scenarios = await self.coordinator.api.get_scenarios()
        _LOGGER.debug("Available scenarios: %s", scenarios)
        
        # Try to run the scenario
        result = await self.coordinator.api.run_scenario(scenario_name)
        _LOGGER.debug("Scenario execution result: %s", result)
        
        if result:
            self._attr_is_on = False
            self.async_write_ha_state()
            # Schedule an immediate update
            await self.coordinator.async_request_refresh()

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        for unit in self.coordinator.data:
            if unit.get("full_id") == self.device.get("full_id"):
                self.device = unit
                self._attr_is_on = unit.get("status", 0) == 1
                self._attr_brightness = unit.get("brightness", 255)
                self.async_write_ha_state()
                break
