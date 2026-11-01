"""Configuration flow for SFR Box Remote."""

import ipaddress
import logging

import voluptuous as vol
import websockets
from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.const import CONF_PORT

from .const import DEFAULT_DEVICE_ID
from .const import DEFAULT_PORT
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

CONF_DEVICE_ID = "device_id"


class SFRBoxRemoteConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SFR Box Remote."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            port = user_input[CONF_PORT]
            device_id = user_input[CONF_DEVICE_ID].strip()

            try:
                parsed_ip = ipaddress.ip_address(host)
            except ValueError:
                errors["base"] = "invalid_host"
            else:
                if not 1 <= port <= 65535:
                    errors["base"] = "invalid_port"
                elif not device_id:
                    errors["base"] = "invalid_host"
                elif any(
                    entry.unique_id == device_id or entry.data.get(CONF_DEVICE_ID) == device_id
                    for entry in self._async_current_entries()
                ):
                    errors["base"] = "already_configured"
                else:
                    websocket_host = f"[{host}]" if parsed_ip.version == 6 else host
                    uri = f"ws://{websocket_host}:{port}/ws"

                    try:
                        websocket = await websockets.connect(uri)
                        await websocket.close()
                    except Exception:
                        _LOGGER.exception(
                            "Unable to connect to SFR Box at %s",
                            uri,
                        )
                        errors["base"] = "cannot_connect"
                    else:
                        return self.async_create_entry(
                            title="SFR Box Remote",
                            data=user_input,
                        )

            user_input[CONF_HOST] = host
            user_input[CONF_DEVICE_ID] = device_id

        data_schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
                vol.Required(
                    CONF_DEVICE_ID,
                    default=DEFAULT_DEVICE_ID,
                ): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )
