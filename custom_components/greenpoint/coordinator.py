"""Data update coordinator for Greenpoint IGH Compact."""
from datetime import timedelta
import logging
from typing import Any, Dict, List, Optional

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import CannotConnect, GreenpointApiClient, InvalidAuth
from .const import DOMAIN, UPDATE_INTERVAL, ATTR_FULL_ID

_LOGGER = logging.getLogger(__name__)


class GreenpointDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(
        self, hass: HomeAssistant, client: GreenpointApiClient, update_interval: int
    ) -> None:
        """Initialize."""
        self.api = client
        self.platforms = []
        self.units = {}
        self.unit_status = {}

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=update_interval),
        )

    async def _async_update_data(self) -> Dict[str, Any]:
        """Update data via API."""
        try:
            # Get all units first
            if not self.units:
                self.units = {
                    unit[ATTR_FULL_ID]: unit for unit in await self.api.get_all_units()
                }

            # Update status for all units
            for unit_id in self.units:
                try:
                    self.unit_status[unit_id] = await self.api.get_unit_status(unit_id)
                except Exception as exception:
                    _LOGGER.error("Error updating status for unit %s: %s", unit_id, exception)

            return {
                "units": self.units,
                "status": self.unit_status,
            }
        except CannotConnect as exception:
            _LOGGER.error("Cannot connect to IGH Compact API: %s", exception)
            raise UpdateFailed("Cannot connect to API") from exception
        except InvalidAuth as exception:
            _LOGGER.error("Invalid authentication: %s", exception)
            raise UpdateFailed("Invalid authentication") from exception
        except Exception as exception:
            _LOGGER.error("Unexpected error: %s", exception)
            raise UpdateFailed(f"Unexpected error: {exception}") from exception
