"""API Client for Greenpoint IGH Compact."""
import logging
from typing import Any, Dict, List, Optional

import aiohttp
from aiohttp import ClientSession

from .const import (
    API_HOME,
    API_SCENARIO,
    API_UNIT,
    ATTR_ROOMS,
    ATTR_UNITS,
)

_LOGGER = logging.getLogger(__name__)

class CannotConnect(Exception):
    """Error to indicate we cannot connect."""

class InvalidAuth(Exception):
    """Error to indicate there is invalid auth."""

class GreenpointApiClient:
    """API Client for Greenpoint IGH Compact."""

    def __init__(
        self,
        host: str,
        port: int,
        token: str,
        session: Optional[ClientSession] = None,
    ) -> None:
        """Initialize the API client."""
        self._host = host
        self._port = port
        self._token = token
        self._session = session
        self._base_url = f"http://{host}:{port}"

    async def test_connection(self) -> bool:
        """Test the connection to the API."""
        try:
            await self.get_home_data()
            return True
        except Exception as e:
            _LOGGER.error("Failed to connect to API: %s", str(e))
            return False

    async def get_home_data(self) -> Dict[str, Any]:
        """Get home data including rooms and units."""
        try:
            async with self._get_session() as session:
                async with session.get(
                    f"{self._base_url}{API_HOME}?token={self._token}"
                ) as response:
                    if response.status == 401:
                        raise InvalidAuth()
                    response.raise_for_status()
                    return await response.json()
        except aiohttp.ClientError as err:
            _LOGGER.error("Error getting home data: %s", err)
            raise CannotConnect() from err

    async def get_unit_list(self) -> List[Dict[str, Any]]:
        """Get list of units from home data."""
        try:
            home_data = await self.get_home_data()
            units = []
            for room in home_data.get(ATTR_ROOMS, []):
                units.extend(room.get(ATTR_UNITS, []))
            return units
        except Exception as err:
            _LOGGER.error("Error getting unit list: %s", err)
            raise CannotConnect() from err

    async def get_unit_status(self, full_id: str) -> Dict[str, Any]:
        """Get unit status."""
        try:
            async with self._get_session() as session:
                async with session.get(
                    f"{self._base_url}{API_UNIT}/{full_id}?token={self._token}"
                ) as response:
                    if response.status == 401:
                        raise InvalidAuth()
                    response.raise_for_status()
                    return await response.json()
        except aiohttp.ClientError as err:
            _LOGGER.error("Error getting unit status: %s", err)
            raise CannotConnect() from err

    async def run_scenario(self, scenario_name: str) -> bool:
        """Run a scenario by name."""
        try:
            async with self._get_session() as session:
                async with session.get(
                    f"{self._base_url}{API_SCENARIO}?name={scenario_name}&token={self._token}"
                ) as response:
                    if response.status == 401:
                        raise InvalidAuth()
                    response.raise_for_status()
                    return True
        except aiohttp.ClientError as err:
            _LOGGER.error("Error running scenario: %s", err)
            raise CannotConnect() from err

    def _get_session(self) -> ClientSession:
        """Get or create aiohttp ClientSession."""
        if self._session is None:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self) -> None:
        """Close the session."""
        if self._session is not None:
            await self._session.close()
            self._session = None

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
