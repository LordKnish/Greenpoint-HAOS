"""Support for Greenpoint IGH Compact switches."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, cast

from homeassistant.components.switch import SwitchEntity
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
    """Set up Greenpoint IGH Compact switches based on config entry."""
    coordinator: GreenpointDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    # Create a list to hold our entities
    entities = []

    # Create switch entities for each unit
    for unit_id, unit_data in coordinator.data["units"].items():
        # Create a device object
        device = GreenpointDevice(unit_id, unit_data)

        # Check if this is a switch type unit (has status)
        status = coordinator.data["status"].get(unit_id, {})
        if ATTR_STATUS in status:
            entities.append(GreenpointSwitch(coordinator, device))

    # Add all entities to Home Assistant
    async_add_entities(entities)


class GreenpointSwitch(GreenpointDeviceEntity, SwitchEntity):
    """Representation of a Greenpoint switch."""

    def __init__(self, coordinator: GreenpointDataUpdateCoordinator, device: GreenpointDevice):
        """Initialize the switch."""
        super().__init__(coordinator, device, "switch")

    @property
    def is_on(self) -> bool | None:
        """Return true if the switch is on."""
        if not self.available:
            return None

        # Assuming status=1 means ON and status=0 means OFF
        # This may need adjustment based on actual API behavior
        return self.device_status.get(ATTR_STATUS) == 1

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        # Create a scenario name based on the device name and "On"
        scenario_name = f"{self.device.name} On"
        
        try:
            await self.coordinator.api.run_scenario(scenario_name)
            # Schedule an immediate data update
            await self.coordinator.async_request_refresh()
        except Exception as exception:
            _LOGGER.error("Failed to turn on %s: %s", self.name, exception)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        # Create a scenario name based on the device name and "Off"
        scenario_name = f"{self.device.name} Off"
        
        try:
            await self.coordinator.api.run_scenario(scenario_name)
            # Schedule an immediate data update
            await self.coordinator.async_request_refresh()
        except Exception as exception:
            _LOGGER.error("Failed to turn off %s: %s", self.name, exception)
