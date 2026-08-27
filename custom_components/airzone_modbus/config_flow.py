"""Config flow for Airzone Modbus."""

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.data_entry_flow import FlowResult

from airzone_modbus.client import AirzoneClient

from .const import DEFAULT_PORT, DOMAIN


class AirzoneModbusConfigFlow(
    config_entries.ConfigFlow,
    domain=DOMAIN,
):
    """Handle an Airzone Modbus config flow."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Handle the user configuration step."""

        errors: dict[str, str] = {}

        if user_input is not None:
            client = None

            try:
                client = AirzoneClient(
                    user_input[CONF_HOST],
                    user_input[CONF_PORT],
                )

                connected = await self.hass.async_add_executor_job(
                    client.connect
                )

                if not connected:
                    errors["base"] = "cannot_connect"
                else:
                    await self.hass.async_add_executor_job(
                        client.read_machine_zones
                    )

                    return self.async_create_entry(
                        title=f"Airzone {user_input[CONF_HOST]}",
                        data=user_input,
                    )

            except Exception:
                errors["base"] = "cannot_connect"

            finally:
                if client is not None:
                    await self.hass.async_add_executor_job(
                        client.close
                    )

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_HOST,
                    default="192.168.1.7",
                ): str,
                vol.Required(
                    CONF_PORT,
                    default=DEFAULT_PORT,
                ): int,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )
