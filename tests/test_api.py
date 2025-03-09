"""Tests for the Greenpoint IGH Compact API client."""
import asyncio
import pytest
from unittest.mock import patch, MagicMock

from custom_components.greenpoint.api import (
    GreenpointApiClient,
    CannotConnect,
    InvalidAuth,
    validate_input,
)
from custom_components.greenpoint.const import ATTR_ROOMS


@pytest.fixture
def mock_session():
    """Fixture to provide a mock aiohttp ClientSession."""
    session = MagicMock()
    return session


@pytest.fixture
def api_client(mock_session):
    """Fixture to provide an API client."""
    return GreenpointApiClient(
        host="192.168.1.100",
        port=20500,
        token="test_token",
        session=mock_session,
    )


async def test_get_home_data(api_client, mock_session):
    """Test getting home data."""
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.json = MagicMock(
        return_value=asyncio.Future()
    )
    mock_response.json.return_value.set_result({
        ATTR_ROOMS: [
            {
                "name": "Living Room",
                "units": [
                    {
                        "name": "Light",
                        "fullId": "light-1",
                    }
                ]
            }
        ]
    })
    mock_session.get = MagicMock(
        return_value=asyncio.Future()
    )
    mock_session.get.return_value.set_result(mock_response)

    result = await api_client.get_home_data()
    
    assert ATTR_ROOMS in result
    assert len(result[ATTR_ROOMS]) == 1
    assert result[ATTR_ROOMS][0]["name"] == "Living Room"
    assert len(result[ATTR_ROOMS][0]["units"]) == 1
    assert result[ATTR_ROOMS][0]["units"][0]["name"] == "Light"
    assert result[ATTR_ROOMS][0]["units"][0]["fullId"] == "light-1"


async def test_get_unit_status(api_client, mock_session):
    """Test getting unit status."""
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.json = MagicMock(
        return_value=asyncio.Future()
    )
    mock_response.json.return_value.set_result({
        "status": 1,
        "mode": 0,
    })
    mock_session.get = MagicMock(
        return_value=asyncio.Future()
    )
    mock_session.get.return_value.set_result(mock_response)

    result = await api_client.get_unit_status("light-1")
    
    assert "status" in result
    assert result["status"] == 1
    assert "mode" in result
    assert result["mode"] == 0


async def test_run_scenario(api_client, mock_session):
    """Test running a scenario."""
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.json = MagicMock(
        return_value=asyncio.Future()
    )
    mock_response.json.return_value.set_result({
        "success": True,
    })
    mock_session.get = MagicMock(
        return_value=asyncio.Future()
    )
    mock_session.get.return_value.set_result(mock_response)

    result = await api_client.run_scenario("Light On")
    
    assert "success" in result
    assert result["success"] is True


async def test_invalid_auth(api_client, mock_session):
    """Test handling invalid authentication."""
    mock_response = MagicMock()
    mock_response.status = 401
    mock_session.get = MagicMock(
        return_value=asyncio.Future()
    )
    mock_session.get.return_value.set_result(mock_response)

    with pytest.raises(InvalidAuth):
        await api_client.get_home_data()


async def test_cannot_connect(api_client, mock_session):
    """Test handling connection errors."""
    import aiohttp
    
    mock_session.get = MagicMock(
        side_effect=aiohttp.ClientError()
    )

    with pytest.raises(CannotConnect):
        await api_client.get_home_data()
