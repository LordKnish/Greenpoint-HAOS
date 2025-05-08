"""The Greenpoint IGH Compact integration."""
from __future__ import annotations

import logging
from typing import Any, Dict

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_TOKEN
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .api import GreenpointApiClient
from .const import DEFAULT_PORT, DOMAIN
from .coordinator import GreenpointDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Greenpoint IGH Compact from a config entry."""
    try:
        # Create API client
        client = GreenpointApiClient(
            host=entry.data[CONF_HOST],
            port=entry.data.get(CONF_PORT, DEFAULT_PORT),
            token=entry.data[CONF_TOKEN],
            session=hass.helpers.aiohttp_client.async_get_clientsession(),
        )

        # Test connection
        if not await client.test_connection():
            raise ConfigEntryNotReady("Could not connect to IGH Compact")

        # Create coordinator
        coordinator = GreenpointDataUpdateCoordinator(hass, client)
        await coordinator.async_config_entry_first_refresh()

        # Store coordinator
        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN][entry.entry_id] = coordinator

        # Set up platforms
        await hass.config_entries.async_forward_entry_setups(entry, ["switch", "light"])

        return True

    except Exception as err:
        _LOGGER.error("Error setting up Greenpoint IGH Compact: %s", err)
        raise ConfigEntryNotReady from err

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["switch", "light"])

    if unload_ok:
        # Remove coordinator
        coordinator: GreenpointDataUpdateCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.api.close()

    return unload_ok
