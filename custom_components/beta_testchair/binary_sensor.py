import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up TestChair sensors from config entry."""
    _LOGGER.debug("🧱 Setting up TestChair binary_sensor platform")

    if DOMAIN not in hass.data or entry.entry_id not in hass.data[DOMAIN]:
        _LOGGER.error("❌ WebSocket client data not found for %s", entry.entry_id)
        return

    # Register async_add_entities callback so websocket client can create entities
    hass.data[DOMAIN][entry.entry_id]["add_binary_sensor_entities"] = async_add_entities


class ServerConnectionBinarySensor(BinarySensorEntity):
    def __init__(self, device_name, unique_id, manufacturer, model, version):
        self._attr_name = f"{device_name} Server Connection"
        self._attr_unique_id = f"{device_name.lower().replace(' ', '_')}_server_connection"
        self._is_connected = True
        self._device_name = device_name
        self._manufacturer = manufacturer
        self._model = model
        self._version = version
        self._unique_id = unique_id

    @property
    def is_on(self):
        return self._is_connected

    def set_connected(self, connected: bool):
        self._is_connected = connected
        self.async_write_ha_state()

    @property
    def device_class(self):
        return "connectivity"  
    
    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._unique_id)},
            "name": self._device_name,
            "manufacturer": self._manufacturer,
            "model": self._model,
            "sw_version": self._version
        }
