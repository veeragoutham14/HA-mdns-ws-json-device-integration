import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up TestChair sensors from config entry."""
    _LOGGER.debug("🧱 Setting up TestChair sensor platform")

    if DOMAIN not in hass.data or entry.entry_id not in hass.data[DOMAIN]:
        _LOGGER.error("❌ WebSocket client data not found for %s", entry.entry_id)
        return

    # Register async_add_entities callback so websocket client can create entities
    hass.data[DOMAIN][entry.entry_id]["add_entities"] = async_add_entities
    

class TestChairSensor(SensorEntity):
    """Representation of a TestChair sensor."""

    def __init__(self, sensor_type: str, initial_value: str, device_name: str, unique_id, manufacturer: str, model: str, version: str):
        """Initialize the sensor."""
        self._attr_name = f"{device_name} {sensor_type.replace('_', ' ').title()}"
        self._attr_unique_id = f"{device_name.lower().replace(' ', '_')}_{sensor_type}"
        self._attr_native_value = initial_value
        self._sensor_type = sensor_type
        self._device_name = device_name
        self._unique_id = unique_id
        self._manufacturer = manufacturer
        self._model = model
        self._version = version
        


    @property
    def device_info(self):

        
        return {
            "identifiers": {(DOMAIN, self._unique_id)},
            "name": self._device_name,
            "manufacturer": self._manufacturer,
            "model": self._model,
            "sw_version": self._version
        }

    def update_value(self, value):
        self._attr_native_value = value
        self.async_write_ha_state()





