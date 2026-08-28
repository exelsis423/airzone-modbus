"""Coordinator for Airzone Modbus."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .client import AirzoneClient

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

        self.client = AirzoneClient(
            host=host,
            port=port,
            slave=slave,
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
            # ----------------------------------------------------
            # MACHINE
            # ----------------------------------------------------

            machine_mode = (
                await self.client.read_machine_mode()
            )

            machine_speed = (
                await self.client.read_machine_speed()
            )

            # ----------------------------------------------------
            # ZONES
            # ----------------------------------------------------

            zones = await self.client.read_zones()

            zone_data = {}

            for zone in zones:
                # -----------------------------------------------
                # R00
                # -----------------------------------------------

                r00 = await self.client.read_zone_r00(
                    zone
                )

                # R00 bits
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
                ) & 0b1111

                automatic_mode = bool(
                    r00 & (1 << 12)
                )

                bit15 = bool(
                    r00 & (1 << 15)
                )

                # -----------------------------------------------
                # R03
                # -----------------------------------------------

                setpoint = (
                    await self.client.read_zone_setpoint(
                        zone
                    )
                )

                # -----------------------------------------------
                # R08
                # -----------------------------------------------

                temperature = (
                    await self.client.read_zone_temperature(
                        zone
                    )
                )

                # -----------------------------------------------
                # R10
                # -----------------------------------------------

                thermostat_temperature = (
                    await self.client.read_zone_thermostat_temperature(
                        zone
                    )
                )

                # -----------------------------------------------
                # R14-R19
                # -----------------------------------------------

                name = (
                    await self.client.read_zone_name(
                        zone
                    )
                )

                # -----------------------------------------------
                # R26
                # -----------------------------------------------

                r26 = await self.client.read_zone_r26(
                    zone
                )

                # Bits 0-2 :
                # 0 -> -3
                # 1 -> -2
                # 2 -> -1
                # 3 ->  0
                # 4 -> +1
                # 5 -> +2
                # 6 -> +3

                thermostat_offset_raw = (
                    r26 & 0b111
                )

                thermostat_offset = (
                    thermostat_offset_raw - 3
                )

                # Bit 3
                thermostat_led = bool(
                    r26 & (1 << 3)
                )

                # Bit 5
                thermostat_lite_present = bool(
                    r26 & (1 << 5)
                )

                # -----------------------------------------------
                # R31
                # -----------------------------------------------

                humidity = (
                    await self.client.read_zone_humidity(
                        zone
                    )
                )

                # -----------------------------------------------
                # STORE ZONE DATA
                # -----------------------------------------------

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

        await self.client.write_machine_mode(
            mode
        )

        await self.async_request_refresh()

    async def async_write_machine_speed(
        self,
        speed: int,
    ) -> None:
        """Write machine speed."""

        await self.client.write_machine_speed(
            speed
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

        await self.client.write_zone_state(
            zone,
            state,
        )

        await self.async_request_refresh()

    async def async_write_zone_automatic_mode(
        self,
        zone: int,
        automatic_mode: bool,
    ) -> None:
        """Write zone automatic mode."""

        await self.client.write_zone_automatic_mode(
            zone,
            automatic_mode,
        )

        await self.async_request_refresh()

    async def async_write_zone_schedule_disabled(
        self,
        zone: int,
        disabled: bool,
    ) -> None:
        """Write zone schedule state."""

        await self.client.write_zone_schedule_disabled(
            zone,
            disabled,
        )

        await self.async_request_refresh()

    async def async_write_zone_mode(
        self,
        zone: int,
        mode: int,
    ) -> None:
        """Write zone mode."""

        await self.client.write_zone_mode(
            zone,
            mode,
        )

        await self.async_request_refresh()

    async def async_write_zone_speed(
        self,
        zone: int,
        speed: int,
    ) -> None:
        """Write zone speed."""

        await self.client.write_zone_speed(
            zone,
            speed,
        )

        await self.async_request_refresh()

    async def async_write_zone_sleep_mode(
        self,
        zone: int,
        sleep_mode: int,
    ) -> None:
        """Write zone sleep mode."""

        await self.client.write_zone_sleep_mode(
            zone,
            sleep_mode,
        )

        await self.async_request_refresh()
