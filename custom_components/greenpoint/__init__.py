"""The Greenpoint IGH Compact integration."""
from __future__ import annotations

import logging
import asyncio
from typing import Any

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import CannotConnect, GreenpointApiClient, InvalidAuth
from .const import (
    DOMAIN,
    CONF_HOST,
    CONF_PORT,
    CONF_TOKEN,
    DEFAULT_PORT,
    UPDATE_INTERVAL,
)
from .coordinator import GreenpointDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# List of platforms to support
PLATFORMS = ["sensor", "binary_sensor", "switch", "light"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Greenpoint IGH Compact from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Get a ClientSession
    session = async_get_clientsession(hass)

    # Create API client
    client = GreenpointApiClient(
        host=entry.data[CONF_HOST],
        port=entry.data.get(CONF_PORT, DEFAULT_PORT),
        token=entry.data[CONF_TOKEN],
        session=session,
    )

    # Validate the API connection (and authentication)
    try:
        if not await client.test_connection():
            raise CannotConnect("Failed to connect to API")
    except CannotConnect as exception:
        _LOGGER.error("Cannot connect to IGH Compact API: %s", exception)
        raise ConfigEntryNotReady from exception
    except InvalidAuth as exception:
        _LOGGER.error("Invalid authentication: %s", exception)
        return False
    except Exception as exception:
        _LOGGER.error("Unexpected exception: %s", exception)
        raise ConfigEntryNotReady from exception

    # Create update coordinator
    scan_interval = entry.options.get("scan_interval", UPDATE_INTERVAL)
    coordinator = GreenpointDataUpdateCoordinator(hass, client, scan_interval)

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    # Store the coordinator
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Set up all platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register options update listener
    entry.async_on_unload(entry.add_update_listener(options_update_listener))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    # Remove config entry from domain
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def options_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)
