"""Support for Greenpoint IGH Compact lights."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, cast

from homeassistant.components.light import LightEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import ATTR_STATUS, DOMAIN
from .coordinator import GreenpointDataUpdateCoordinator
from .device import GreenpointDevice, GreenpointDeviceEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Greenpoint IGH Compact lights based on config entry."""
    coordinator: GreenpointDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    # Create a list to hold our entities
    entities = []

    # Create light entities for each unit
    for unit_id, unit_data in coordinator.data["units"].items():
        # Create a device object
        device = GreenpointDevice(unit_id, unit_data)

        # Check if this is a light unit (name contains "Light")
        # This is a simple heuristic and may need adjustment based on actual API behavior
        if "Light" in device.name and ATTR_STATUS in coordinator.data["status"].get(unit_id, {}):
            entities.append(GreenpointLight(coordinator, device))

    # Add all entities to Home Assistant
    async_add_entities(entities)


class GreenpointLight(GreenpointDeviceEntity, LightEntity):
    """Representation of a Greenpoint light."""

    def __init__(self, coordinator: GreenpointDataUpdateCoordinator, device: GreenpointDevice):
        """Initialize the light."""
        super().__init__(coordinator, device, "light")

    @property
    def is_on(self) -> bool | None:
        """Return true if the light is on."""
        if not self.available:
            return None

        # For IGHX light units, the API documentation mentions using bitwise flag operation
        # This is a simplified implementation and may need adjustment based on actual API behavior
        return self.device_status.get(ATTR_STATUS) > 0

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the light on."""
        # Create a scenario name based on the device name and "On"
        scenario_name = f"{self.device.name} On"
        
        try:
            await self.coordinator.api.run_scenario(scenario_name)
            # Schedule an immediate data update
            await self.coordinator.async_request_refresh()
        except Exception as exception:
            _LOGGER.error("Failed to turn on %s: %s", self.name, exception)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the light off."""
        # Create a scenario name based on the device name and "Off"
        scenario_name = f"{self.device.name} Off"
        
        try:
            await self.coordinator.api.run_scenario(scenario_name)
            # Schedule an immediate data update
            await self.coordinator.async_request_refresh()
        except Exception as exception:
            _LOGGER.error("Failed to turn off %s: %s", self.name, exception)
