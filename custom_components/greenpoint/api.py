"""API client for Greenpoint IGH Compact."""
import logging
import aiohttp
import async_timeout
from typing import Dict, List, Any, Optional

from .const import (
    API_HOME,
    API_SCENARIO,
    API_UNIT,
    ATTR_ROOMS,
    ATTR_UNITS,
    ATTR_NAME,
    ATTR_FULL_ID,
)

_LOGGER = logging.getLogger(__name__)

class CannotConnect(Exception):
    """Error to indicate we cannot connect."""

class InvalidAuth(Exception):
    """Error to indicate there is invalid auth."""

class GreenpointApiClient:
    """API client for Greenpoint IGH Compact."""

    def __init__(self, host: str, port: int, token: str, session: aiohttp.ClientSession):
        """Initialize the API client."""
        self.host = host
        self.port = port
        self.token = token
        self.session = session
        self.base_url = f"http://{host}:{port}"

    async def test_connection(self) -> bool:
        """Test connectivity to the API."""
        try:
            await self.get_home_data()
            return True
        except Exception as exception:
            _LOGGER.error("Connection test failed: %s", exception)
            return False

    async def get_home_data(self) -> Dict[str, Any]:
        """Get home data from the API."""
        return await self._api_request(f"{API_HOME}?token={self.token}")

    async def get_unit_status(self, full_id: str) -> Dict[str, Any]:
        """Get unit status from the API."""
        return await self._api_request(f"{API_UNIT}/{full_id}?token={self.token}")

    async def run_scenario(self, scene_name: str) -> Dict[str, Any]:
        """Run a scenario by name."""
        return await self._api_request(f"{API_SCENARIO}?name={scene_name}&token={self.token}")

    async def get_all_units(self) -> List[Dict[str, Any]]:
        """Get all units from all rooms."""
        home_data = await self.get_home_data()
        units = []

        if ATTR_ROOMS not in home_data:
            _LOGGER.error("No rooms found in home data")
            return units

        for room in home_data[ATTR_ROOMS]:
            if ATTR_UNITS in room:
                for unit in room[ATTR_UNITS]:
                    # Add room name to unit data for reference
                    unit["room_name"] = room.get(ATTR_NAME, "Unknown Room")
                    units.append(unit)

        return units

    async def _api_request(self, endpoint: str) -> Dict[str, Any]:
        """Make a request to the API."""
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with async_timeout.timeout(10):
                response = await self.session.get(url)
                
                if response.status == 401:
                    raise InvalidAuth("Invalid authentication")
                
                response.raise_for_status()
                return await response.json()
                
        except aiohttp.ClientResponseError as exception:
            _LOGGER.error("Error fetching data: %s", exception)
            raise
        except aiohttp.ClientError as exception:
            _LOGGER.error("Error connecting to API: %s", exception)
            raise CannotConnect() from exception
        except Exception as exception:
            _LOGGER.error("Unexpected error: %s", exception)
            raise

async def validate_input(host: str, port: int, token: str) -> Dict[str, Any]:
    """Validate the user input allows us to connect."""
    async with aiohttp.ClientSession() as session:
        client = GreenpointApiClient(host, port, token, session)
        
        try:
            home_data = await client.get_home_data()
            
            # Check if we got valid data
            if ATTR_ROOMS not in home_data:
                raise CannotConnect("Invalid response from API")
                
            # Return info that you want to store in the config entry.
            return {"title": f"IGH Compact ({host})"}
            
        except CannotConnect as exception:
            _LOGGER.error("Cannot connect to IGH Compact: %s", exception)
            raise
        except InvalidAuth as exception:
            _LOGGER.error("Invalid authentication: %s", exception)
            raise
        except Exception as exception:
            _LOGGER.error("Unexpected exception: %s", exception)
            raise
