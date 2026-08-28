"""Coordinator for Airzone Modbus."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from airzone_modbus.client import AirzoneClient

_LOGGER = logging.getLogger(__name__)


class AirzoneCoordinator(
    DataUpdateCoordinator[dict],
):
    """Coordinator for Airzone Modbus."""

    def __init__(
        self,
        hass: HomeAssistant,
        host: str,
        port: int,
        slave: int,
        update_interval: int,
    ) -> None:
        """Initialize the coordinator."""

        self.hass = hass
        self.slave = slave

        self.client = AirzoneClient(
            host=host,
            port=port,
        )

        super().__init__(
            hass,
            _LOGGER,
            name="Airzone Modbus",
            update_interval=timedelta(
                seconds=update_interval
            ),
        )

    # ============================================================
    # UPDATE
    # ============================================================

    async def _async_update_data(self) -> dict:
        """Read all Airzone data."""

        try:
            await self.hass.async_add_executor_job(
                self.client.connect
            )

            machine_mode = (
                await self.hass.async_add_executor_job(
                    self.client.read_machine_mode,
                    self.slave,
                )
            )

            machine_speed = (
                await self.hass.async_add_executor_job(
                    self.client.read_machine_speed,
                    self.slave,
                )
            )

            zones = (
                await self.hass.async_add_executor_job(
                    self.client.read_machine_zones,
                    self.slave,
                )
            )

            zone_data = {}

            for zone in zones:
                base = zone * 256

                # ------------------------------------------------
                # R00
                # ------------------------------------------------

                r00 = (
                    await self.hass.async_add_executor_job(
                        self.client.read_zone_r00,
                        base,
                        self.slave,
                    )
                )

                local_ventilation = bool(
                    r00 & (1 << 0)
                )

                schedule_disabled = bool(
                    r00 & (1 << 1)
                )

                state = bool(
                    r00 & (1 << 2)
                )

                speed = (
                    r00 >> 4
                ) & 0b11

                sleep_mode = (
                    r00 >> 6
                ) & 0b11

                mode = (
                    r00 >> 8
                ) & 0x0F

                automatic_mode = bool(
                    r00 & (1 << 12)
                )

                bit15 = bool(
                    r00 & (1 << 15)
                )

                # ------------------------------------------------
                # R03
                # ------------------------------------------------

                setpoint = (
                    await self.hass.async_add_executor_job(
                        self.client.read_zone_setpoint,
                        base,
                        self.slave,
                    )
                )

                # ------------------------------------------------
                # R08
                # ------------------------------------------------

                temperature = (
                    await self.hass.async_add_executor_job(
                        self.client.read_zone_temperature,
                        base,
                        self.slave,
                    )
                )

                # ------------------------------------------------
                # R10
                # ------------------------------------------------

                thermostat_temperature = (
                    await self.hass.async_add_executor_job(
                        self.client.read_zone_thermostat_temperature,
                        base,
                        self.slave,
                    )
                )

                # ------------------------------------------------
                # R14-R19
                # ------------------------------------------------

                name = (
                    await self.hass.async_add_executor_job(
                        self.client.read_zone_name,
                        base,
                        self.slave,
                    )
                )

                # ------------------------------------------------
                # R26
                # ------------------------------------------------

                r26 = (
                    await self.hass.async_add_executor_job(
                        self.client.read_zone_r26,
                        base,
                        self.slave,
                    )
                )

                thermostat_offset = (
                    self.client.decode_thermostat_lite_offset(
                        r26
                    )
                )

                thermostat_led = (
                    self.client.decode_thermostat_lite_led(
                        r26
                    )
                )

                thermostat_lite_present = (
                    self.client.decode_thermostat_lite_present(
                        r26
                    )
                )

                # ------------------------------------------------
                # R31
                # ------------------------------------------------

                humidity = (
                    await self.hass.async_add_executor_job(
                        self.client.read_zone_humidity,
                        base,
                        self.slave,
                    )
                )

                zone_data[zone] = {
                    # R00
                    "local_ventilation": (
                        local_ventilation
                    ),
                    "schedule_disabled": (
                        schedule_disabled
                    ),
                    "state": state,
                    "speed": speed,
                    "sleep_mode": sleep_mode,
                    "mode": mode,
                    "automatic_mode": (
                        automatic_mode
                    ),
                    "bit15": bit15,

                    # R03
                    "setpoint": setpoint,

                    # R08
                    "temperature": temperature,

                    # R10
                    "thermostat_temperature": (
                        thermostat_temperature
                    ),

                    # R14-R19
                    "name": name,

                    # R26
                    "thermostat_offset": (
                        thermostat_offset
                    ),
                    "thermostat_led": (
                        thermostat_led
                    ),
                    "thermostat_lite_present": (
                        thermostat_lite_present
                    ),

                    # R31
                    "humidity": humidity,
                }

            return {
                "machine": {
                    "mode": machine_mode,
                    "speed": machine_speed,
                },
                "zones": zones,
                "zone_data": zone_data,
            }

        except Exception as err:
            raise UpdateFailed(
                f"Erreur de communication avec Airzone: {err}"
            ) from err

    # ============================================================
    # MACHINE - WRITE
    # ============================================================

    async def async_write_machine_mode(
        self,
        mode: int,
    ) -> None:
        """Write machine mode."""

        await self.hass.async_add_executor_job(
            self.client.write_machine_mode,
            mode,
            self.slave,
        )

        await self.async_request_refresh()

    async def async_write_machine_speed(
        self,
        speed: int,
    ) -> None:
        """Write machine speed."""

        await self.hass.async_add_executor_job(
            self.client.write_machine_speed,
            speed,
            self.slave,
        )

        await self.async_request_refresh()

    # ============================================================
    # ZONE - R00 WRITE
    # ============================================================

    async def async_write_zone_state(
        self,
        zone: int,
        state: bool,
    ) -> None:
        """Write zone state."""

        await self.hass.async_add_executor_job(
            self.client.write_zone_state,
            zone * 256,
            state,
            self.slave,
        )

        await self.async_request_refresh()

    async def async_write_zone_automatic_mode(
        self,
        zone: int,
        automatic_mode: bool,
    ) -> None:
        """Write zone automatic mode."""

        await self.hass.async_add_executor_job(
            self.client.write_zone_automatic_mode,
            zone * 256,
            automatic_mode,
            self.slave,
        )

        await self.async_request_refresh()

    async def async_write_zone_schedule_disabled(
        self,
        zone: int,
        disabled: bool,
    ) -> None:
        """Write zone schedule state."""

        await self.hass.async_add_executor_job(
            self.client.write_zone_schedule_disabled,
            zone * 256,
            disabled,
            self.slave,
        )

        await self.async_request_refresh()

    async def async_write_zone_mode(
        self,
        zone: int,
        mode: int,
    ) -> None:
        """Write zone mode."""

        await self.hass.async_add_executor_job(
            self.client.write_zone_mode,
            zone * 256,
            mode,
            self.slave,
        )

        await self.async_request_refresh()

    async def async_write_zone_speed(
        self,
        zone: int,
        speed: int,
    ) -> None:
        """Write zone speed."""

        await self.hass.async_add_executor_job(
            self.client.write_zone_speed,
            zone * 256,
            speed,
            self.slave,
        )

        await self.async_request_refresh()

    async def async_write_zone_sleep_mode(
        self,
        zone: int,
        sleep_mode: int,
    ) -> None:
        """Write zone sleep mode."""

        await self.hass.async_add_executor_job(
            self.client.write_zone_sleep_mode,
            zone * 256,
            sleep_mode,
            self.slave,
        )

        await self.async_request_refresh()
