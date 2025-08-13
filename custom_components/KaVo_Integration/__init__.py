import logging
from .websocket_client import websocketclient
from homeassistant.helpers import device_registry as dr
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN

PLATFORMS = ["sensor", "binary_sensor", "calendar"]  #allows integration to load platform sensor


_LOGGER = logging.getLogger(__name__)
_LOGGER.warning("custom integration loaded")



async def async_setup(hass, config):
    _LOGGER.warning("async_setup called")
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    _LOGGER.warning("async_setup_entry called")

    # --- Get connection info
    host = entry.data["host"]
    hostname = entry.data["hostname"]
    port = entry.data["port"]
    entry_id = entry.entry_id


    # --- Create and store WebSocket client
    client = websocketclient(hass, host, hostname, port, entry_id)
    

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry_id] = {
        "client": client,
        "sensors": {},  # We'll use this to store sensor entities
        "binary_sensors": {},
        "add_entities": None,
        "add_binary_sensor_entities": None,
        "calendar_entity": None,
        "add_calendar_entities": None,
        "device_name": entry.title,
        "manufacturer": entry.data.get("manufacturer", "KaVo"),
        "model": entry.data.get("model", "SmartChair-X"),
        "version": entry.data.get("version", "1.0"),
        "unique_id": entry.unique_id
    }

    

    # --- Register the device in the device registry
    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
    config_entry_id=entry.entry_id,
    identifiers={(DOMAIN, entry.unique_id)},  # ← Must match entity's device_info
    manufacturer=entry.data["manufacturer"],
    model=entry.data["model"],
    name=entry.title.replace("._kavochair._tcp.local.", ""),
    sw_version=entry.data["version"]
    )

    # Forward entry to needed platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    #await client.connect()
    hass.async_create_task(client.connect())
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload an entry."""
    entry_data = hass.data[DOMAIN].pop(entry.entry_id, None)
    if entry_data and entry_data["client"]:
        await entry_data["client"].disconnect()

    return True
