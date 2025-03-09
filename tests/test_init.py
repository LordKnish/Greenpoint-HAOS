"""Tests for the Greenpoint IGH Compact integration setup."""
from unittest.mock import patch, MagicMock

import pytest

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component

from custom_components.greenpoint.const import DOMAIN
from custom_components.greenpoint.api import CannotConnect, InvalidAuth


async def test_setup_entry(hass: HomeAssistant):
    """Test setting up the integration."""
    # Create a mock entry
    entry = MagicMock()
    entry.data = {
        "host": "192.168.1.100",
        "port": 20500,
        "token": "test_token",
    }
    entry.entry_id = "test_entry_id"
    entry.options = {}

    # Mock the API client
    mock_client = MagicMock()
    mock_client.test_connection.return_value = True

    # Mock the coordinator
    mock_coordinator = MagicMock()
    mock_coordinator.async_config_entry_first_refresh = MagicMock(
        return_value=True
    )

    # Patch the API client and coordinator
    with patch(
        "custom_components.greenpoint.api.GreenpointApiClient",
        return_value=mock_client,
    ), patch(
        "custom_components.greenpoint.coordinator.GreenpointDataUpdateCoordinator",
        return_value=mock_coordinator,
    ), patch(
        "homeassistant.config_entries.ConfigEntries.async_forward_entry_setups",
        return_value=True,
    ):
        # Test successful setup
        from custom_components.greenpoint import async_setup_entry

        assert await async_setup_entry(hass, entry)
        assert DOMAIN in hass.data
        assert entry.entry_id in hass.data[DOMAIN]


async def test_setup_entry_cannot_connect(hass: HomeAssistant):
    """Test setting up the integration with connection error."""
    # Create a mock entry
    entry = MagicMock()
    entry.data = {
        "host": "192.168.1.100",
        "port": 20500,
        "token": "test_token",
    }
    entry.entry_id = "test_entry_id"
    entry.options = {}

    # Mock the API client
    mock_client = MagicMock()
    mock_client.test_connection.side_effect = CannotConnect("Cannot connect")

    # Patch the API client
    with patch(
        "custom_components.greenpoint.api.GreenpointApiClient",
        return_value=mock_client,
    ), pytest.raises(Exception):
        # Test setup with connection error
        from custom_components.greenpoint import async_setup_entry

        await async_setup_entry(hass, entry)


async def test_setup_entry_invalid_auth(hass: HomeAssistant):
    """Test setting up the integration with invalid auth."""
    # Create a mock entry
    entry = MagicMock()
    entry.data = {
        "host": "192.168.1.100",
        "port": 20500,
        "token": "test_token",
    }
    entry.entry_id = "test_entry_id"
    entry.options = {}

    # Mock the API client
    mock_client = MagicMock()
    mock_client.test_connection.side_effect = InvalidAuth("Invalid auth")

    # Patch the API client
    with patch(
        "custom_components.greenpoint.api.GreenpointApiClient",
        return_value=mock_client,
    ):
        # Test setup with invalid auth
        from custom_components.greenpoint import async_setup_entry

        assert not await async_setup_entry(hass, entry)


async def test_unload_entry(hass: HomeAssistant):
    """Test unloading the integration."""
    # Create a mock entry
    entry = MagicMock()
    entry.entry_id = "test_entry_id"

    # Set up the integration data
    hass.data[DOMAIN] = {entry.entry_id: MagicMock()}

    # Patch the unload platforms method
    with patch(
        "homeassistant.config_entries.ConfigEntries.async_unload_platforms",
        return_value=True,
    ):
        # Test successful unload
        from custom_components.greenpoint import async_unload_entry

        assert await async_unload_entry(hass, entry)
        assert entry.entry_id not in hass.data[DOMAIN]
