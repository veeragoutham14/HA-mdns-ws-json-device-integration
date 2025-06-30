import logging
from typing import Any

from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.data_entry_flow import FlowResult
import voluptuous as vol

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
_LOGGER.warning("✅ TestChair config_flow.py loaded")


class TestChairConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for TestChair."""

    VERSION = 1

    def __init__(self):
        self.discovery_info: dict[str, Any] = {}
        _LOGGER.warning("✅ TestChairConfigFlow instance created")

    async def async_step_zeroconf(self, discovery_info: dict[str, Any]) -> FlowResult:
        """Handle Zeroconf discovery."""
        _LOGGER.warning("🔍 async_step_zeroconf called with: %s", discovery_info)

        host = discovery_info.host
        name = discovery_info.name
        hostname = discovery_info.hostname
        device_manufacturer = discovery_info.properties.get("manufacturer","KaVo")
        device_model = discovery_info.properties.get("model","Smart_Chair-X")
        device_version = discovery_info.properties.get("version","1.0")
        
        
        

        await self.async_set_unique_id(name)
        self._abort_if_unique_id_configured(updates={CONF_HOST: host})

        self.context.update({
            "title_placeholders": {
                "name": name.replace("._testkavo._tcp.local.", "")
            }
        })

        self.discovery_info = {
            "host": host,
            "port": discovery_info.port,
            "hostname": hostname,
            "name": name,
            "manufacturer": device_manufacturer,
            "model": device_model,
            "version": device_version
        }

        return await self.async_step_zeroconf_confirm()

    async def async_step_zeroconf_confirm(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Confirm discovery before setting up entry."""
        _LOGGER.warning("🧾 async_step_zeroconf_confirm called")

        if user_input is not None:
            _LOGGER.warning("✅ Discovery confirmed by user")
            cleaned_name = self.discovery_info["name"].replace("._testkavo._tcp.local.", "")
            return self.async_create_entry(
                title= cleaned_name,
                data={
                    "host": self.discovery_info["host"],
                    "port": self.discovery_info["port"],
                    "name": cleaned_name,
                    "manufacturer": self.discovery_info["manufacturer"],
                    "model": self.discovery_info["model"],
                    "version": self.discovery_info["version"]
                },
            )

        self._set_confirm_only()
        return self.async_show_form(step_id="zeroconf_confirm")

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Manual configuration step."""
        _LOGGER.warning("🧑‍💻 async_step_user called")
        errors = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            _LOGGER.warning("📥 Manual input: %s", host)
            await self.async_set_unique_id(host, raise_on_progress=False)
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title="Test Chair",
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required("host"): str,
            vol.Required("port",default=8080): int}),
            errors=errors,
        )
