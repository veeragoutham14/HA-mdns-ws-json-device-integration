import asyncio
import logging
import websockets
import json
from homeassistant.util import dt as dt_util
from datetime import timedelta
from homeassistant.core import HomeAssistant, callback
from .sensor import TestChairSensor
from .binary_sensor import ServerConnectionBinarySensor
from .calendar import HygieneCalendar
from .const import DOMAIN


_LOGGER = logging.getLogger(__name__)


class websocketclient:
    
    def __init__(self, hass:HomeAssistant, host:str, hostname:str, port:int, entry_id:str):
        self.hass = hass
        self.host = host
        self.hostname = hostname
        self.port = port
        self.websocket = None
        self.entry_id = entry_id
        self.server_connection_status = None
        self.server_connection_entity = None
        

    async def connect(self):

        retry_delay_time = 5

        while True:
            try:

                
                url = f"ws://{self.host}:{self.port}"
                _LOGGER.info("🔌 Connecting to WebSocket at %s", url)
                self.websocket = await websockets.connect(url)
                _LOGGER.info("✅ Connection with server successful")

                if self.server_connection_status is None:
                    
                    integration_data_for_server = self.hass.data[DOMAIN][self.entry_id]
                    _LOGGER.info(f"integration data for server connection:{integration_data_for_server}")
                    device_name = integration_data_for_server.get("device_name", "Test Chair")
                    device_manufacturer = integration_data_for_server.get("manufacturer", "kavo")
                    device_model = integration_data_for_server.get("model","sample-x")
                    device_version = integration_data_for_server.get("version","sample version")
                    device_unique_id = integration_data_for_server.get("unique_id")
                    binary_sensors = integration_data_for_server.get("binary_sensors", {})
                    binary_add = integration_data_for_server.get("add_binary_sensor_entities")

                    new_entities = []
                    self.server_connection_status = ServerConnectionBinarySensor(device_name, device_unique_id, device_manufacturer, device_model, device_version)
                    _LOGGER.info(f"server_connection_status instance:{self.server_connection_status}")
                    binary_sensors["Server_Connection"] = self.server_connection_status
                    new_entities.append(self.server_connection_status)
                    
                    
                    if new_entities and binary_add:
                        binary_add(new_entities)
                        self.server_connection_status.set_connected(True)
                else:
                    self.server_connection_status.set_connected(True)

                
                asyncio.create_task(self.listen())
                return
                
            except Exception as e:
                _LOGGER.error("error while connecting to webserver: %s", e)

            _LOGGER.warning("🔌 WebSocket disconnected. Retrying in %s seconds...", retry_delay_time)
            
            if self.server_connection_status:
                self.server_connection_status.set_connected(False)    
            
            await asyncio.sleep(retry_delay_time)

    async def listen(self):
        
        try:

            async for message in self.websocket:
                _LOGGER.info("📩 Received message: %s",message)
                await self.handle_message(message)

        except websockets.exceptions.ConnectionClosed:
            _LOGGER.warning("🚫 WebSocket connection closed.")
        except Exception as e:
            _LOGGER.error("error while reciving message: %s", e)

        finally:
            await self.connect()


    async def handle_message(self, message: str):

        try:
            data = json.loads(message)
            _LOGGER.info("🔍 Parsed JSON data: %s", data)

            # Debug entry_id usage
            if DOMAIN not in self.hass.data:
                    _LOGGER.error("🔍 DOMAIN not found in hass.data")
                    return
            if self.entry_id not in self.hass.data[DOMAIN]:
                    _LOGGER.error("🔍 Entry ID %s not found in DOMAIN data", self.entry_id)
                    return

            integration_data = self.hass.data[DOMAIN][self.entry_id]
            _LOGGER.info("intgratioion_data: %s", integration_data)
            sensors = integration_data.get("sensors", {})
            add_entities = integration_data.get("add_entities")
            calendar_entity = integration_data.get("calendar_entity")
            
            device_name = integration_data.get("device_name", "Test Chair")
            device_manufacturer = integration_data.get("manufacturer", "kavo")
            device_model = integration_data.get("model","sample-x")
            device_version = integration_data.get("version","sample version")
            device_unique_id = integration_data.get("unique_id")
            
            # Separate normal sensor data and calendar event data
            normal_sensor_data = {}
            
            
            for key, value in data.items():
                if key.startswith("CAL"):
                    existing_event = next((e for e in calendar_entity._events if e.uid == key), None)

                    if value:
                        # Value is not empty, so create or update
                        start_time_nr = dt_util.parse_datetime(value)
                        start_time = dt_util.as_local(start_time_nr)
                        #start_time = dt_util.as_utc(start_time)
                        end_time = start_time + timedelta(minutes=3) if start_time else None

                        if start_time and end_time and calendar_entity:
                            if existing_event:
                                # UPDATE the existing event
                                await calendar_entity.async_update_event(
                                    uid=key,
                                    event={
                                        "summary": key.removeprefix("CAL_").replace("_", " ").title(),
                                        "start": start_time,
                                        "end": end_time,
                                        "description": f"Hygiene Event: {key}",
                                        "location": "Dental Chair Room",
                                    },)
                            else:
                                # CREATE a new event
                                await calendar_entity.async_create_event(
                                    uid=key,
                                    summary= key.removeprefix("CAL_").replace("_", " ").title(),
                                    start=start_time,
                                    end=end_time,
                                    description=f"Hygiene Event: {key}",
                                    location="Dental Chair Room",
                                )
                    else:
                        # Value is empty --> DELETE the event if it exists
                        if existing_event:
                            await calendar_entity.async_delete_event(uid=key)

                else:
                    normal_sensor_data[key] = value
            
            new_entities = []
            for key, value in normal_sensor_data.items():
                if key not in sensors:
                    sensor = TestChairSensor(key, value, device_name, device_unique_id, device_manufacturer, device_model, device_version)
                    sensors[key] = sensor
                    new_entities.append(sensor)
                else:
                    sensors[key].update_value(value)

            if new_entities and add_entities:
                add_entities(new_entities)

            
            

        except json.JSONDecodeError:
            _LOGGER.warning("Received non-JSON message: %s", message)
                
    async def disconnect(self):
        """Cleanly close the WebSocket connection and stop reconnect attempts."""
        _LOGGER.warning("🔌 Disconnecting WebSocket client")

        if self.websocket is not None:
            try:
                await self.websocket.close()
                _LOGGER.info("✅ WebSocket connection closed successfully")
            except Exception as e:
                _LOGGER.error("❌ Error while closing WebSocket: %s", e)
            finally:
                self.websocket = None
