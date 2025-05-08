"""Data update coordinator for Greenpoint IGH Compact."""
from datetime import timedelta
import logging
from typing import Any, Dict, List, Optional

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import CannotConnect, GreenpointApiClient, InvalidAuth
from .const import DOMAIN, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)


class GreenpointDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(
        self, hass: HomeAssistant, client: GreenpointApiClient
    ) -> None:
        """Initialize."""
        self.api = client
        self.platforms = []

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )

    async def _async_update_data(self) -> List[Dict[str, Any]]:
        """Update data via API."""
        try:
            # Get all units
            units = await self.api.get_unit_list()
            
            # Update status for each unit
            for unit in units:
                try:
                    status = await self.api.get_unit_status(unit["full_id"])
                    unit.update(status)
                except Exception as exception:
                    _LOGGER.error("Error updating status for unit %s: %s", unit["full_id"], exception)

            return units
        except CannotConnect as exception:
            _LOGGER.error("Cannot connect to IGH Compact API: %s", exception)
            raise UpdateFailed("Cannot connect to API") from exception
        except InvalidAuth as exception:
            _LOGGER.error("Invalid authentication: %s", exception)
            raise UpdateFailed("Invalid authentication") from exception
        except Exception as exception:
            _LOGGER.error("Unexpected error: %s", exception)
            raise UpdateFailed(f"Unexpected error: {exception}") from exception
