"""Device management for Greenpoint IGH Compact."""
import logging
from typing import Dict, List, Optional, Any

from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, ATTR_NAME, ATTR_FULL_ID

_LOGGER = logging.getLogger(__name__)


class GreenpointDevice:
    """Representation of a Greenpoint device."""

    def __init__(self, unit_id: str, unit_data: Dict[str, Any]):
        """Initialize the device."""
        self.unit_id = unit_id
        self.unit_data = unit_data
        self.name = unit_data.get(ATTR_NAME, "Unknown")
        self.room_name = unit_data.get("room_name", "Unknown Room")
        self.device_info = self._get_device_info()

    def _get_device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.unit_id)},
            name=f"{self.room_name} {self.name}",
            manufacturer="Greenpoint",
            model="IGH Compact",
            via_device=(DOMAIN, "hub"),
        )

    def update_data(self, unit_data: Dict[str, Any]) -> None:
        """Update device data."""
        self.unit_data = unit_data
        self.name = unit_data.get(ATTR_NAME, self.name)
        self.room_name = unit_data.get("room_name", self.room_name)


class GreenpointDeviceEntity(CoordinatorEntity):
    """Base entity for Greenpoint devices."""

    def __init__(self, coordinator, device: GreenpointDevice, entity_type: str):
        """Initialize the entity."""
        super().__init__(coordinator)
        self.device = device
        self.entity_type = entity_type
        self._attr_device_info = device.device_info
        self._attr_unique_id = f"{device.unit_id}_{entity_type}"
        self._attr_name = f"{device.room_name} {device.name} {entity_type.capitalize()}"

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        if not self.coordinator.last_update_success:
            return False
            
        # Check if we have status data for this device
        if self.device.unit_id not in self.coordinator.data.get("status", {}):
            return False
            
        return True

    @property
    def device_status(self) -> Dict[str, Any]:
        """Return the device status."""
        if not self.available:
            return {}
            
        return self.coordinator.data["status"].get(self.device.unit_id, {})
