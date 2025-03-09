"""Support for Greenpoint IGH Compact binary sensors."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, cast

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import ATTR_SPAN_SECOND, DOMAIN
from .coordinator import GreenpointDataUpdateCoordinator
from .device import GreenpointDevice, GreenpointDeviceEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Greenpoint IGH Compact binary sensors based on config entry."""
    coordinator: GreenpointDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    # Create a list to hold our entities
    entities = []

    # Create binary sensor entities for each unit
    for unit_id, unit_data in coordinator.data["units"].items():
        # Create a device object
        device = GreenpointDevice(unit_id, unit_data)

        # Check if this is a motion sensor (has span_second)
        status = coordinator.data["status"].get(unit_id, {})
        if ATTR_SPAN_SECOND in status:
            entities.append(GreenpointMotionSensor(coordinator, device))

    # Add all entities to Home Assistant
    async_add_entities(entities)


class GreenpointMotionSensor(GreenpointDeviceEntity, BinarySensorEntity):
    """Representation of a Greenpoint motion sensor."""

    _attr_device_class = BinarySensorDeviceClass.MOTION

    def __init__(self, coordinator: GreenpointDataUpdateCoordinator, device: GreenpointDevice):
        """Initialize the binary sensor."""
        super().__init__(coordinator, device, "motion")

    @property
    def is_on(self) -> bool | None:
        """Return true if motion is detected."""
        if not self.available:
            return None

        # If span_second is less than 30, consider motion detected
        # This is a simple heuristic and may need adjustment based on actual API behavior
        span_second = self.device_status.get(ATTR_SPAN_SECOND, 0)
        return span_second < 30
