"""Support for Greenpoint IGH Compact sensors."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import ATTR_TEMP, DOMAIN
from .coordinator import GreenpointDataUpdateCoordinator
from .device import GreenpointDevice, GreenpointDeviceEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Greenpoint IGH Compact sensors based on config entry."""
    coordinator: GreenpointDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    # Create a list to hold our entities
    entities = []

    # Create sensor entities for each unit
    for unit_id, unit_data in coordinator.data["units"].items():
        # Create a device object
        device = GreenpointDevice(unit_id, unit_data)

        # Check if this is a sensor type unit (has temperature)
        status = coordinator.data["status"].get(unit_id, {})
        if ATTR_TEMP in status:
            entities.append(GreenpointTemperatureSensor(coordinator, device))

    # Add all entities to Home Assistant
    async_add_entities(entities)


class GreenpointTemperatureSensor(GreenpointDeviceEntity, SensorEntity):
    """Representation of a Greenpoint temperature sensor."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    def __init__(self, coordinator: GreenpointDataUpdateCoordinator, device: GreenpointDevice):
        """Initialize the sensor."""
        super().__init__(coordinator, device, "temperature")

    @property
    def native_value(self) -> float | None:
        """Return the temperature."""
        if not self.available:
            return None

        return self.device_status.get(ATTR_TEMP)
