"""Coordinator Airzone Modbus."""

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from airzone_modbus.client import AirzoneClient

from .const import (
    DEFAULT_PORT,
    DEFAULT_SLAVE,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class AirzoneCoordinator(DataUpdateCoordinator):
    """Coordonne les données Airzone."""

    def __init__(
        self,
        hass: HomeAssistant,
        host: str,
        port: int = DEFAULT_PORT,
        slave: int = DEFAULT_SLAVE,
        update_interval: int = DEFAULT_UPDATE_INTERVAL,
    ) -> None:
        self.client = AirzoneClient(host, port)
        self.slave = slave

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(
                seconds=update_interval
            ),
        )

    async def _async_update_data(self):
        """Récupère les données Airzone."""
        try:
            return await self.hass.async_add_executor_job(
                self._update_data
            )

        except Exception as err:
            raise UpdateFailed(
                f"Erreur de communication avec Airzone : {err}"
            ) from err

    def _update_data(self):
        """Lecture synchrone des données."""
        if not self.client.connect():
            raise RuntimeError(
                "Impossible de se connecter à Airzone"
            )

        try:
            # ========================================================
            # MACHINE
            # ========================================================

            zones = self.client.read_machine_zones(
                slave=self.slave,
            )

            machine_mode = self.client.read_machine_mode_name(
                slave=self.slave,
            )

            machine_speed = self.client.read_machine_speed_name(
                slave=self.slave,
            )

            # ========================================================
            # ZONES
            # ========================================================

            zone_data = {}

            for zone in zones:
                base_address = zone * 256

                zone_data[zone] = {
                    # ------------------------------------------------
                    # R00 - BIT 0
                    # Ventilation locale
                    # ------------------------------------------------
                    "local_ventilation": (
                        self.client.read_zone_local_ventilation(
                            base_address,
                            slave=self.slave,
                        )
                    ),

                    # ------------------------------------------------
                    # R00 - BIT 1
                    # Programmation désactivée
                    # ------------------------------------------------
                    "schedule_disabled": (
                        self.client.read_zone_schedule_disabled(
                            base_address,
                            slave=self.slave,
                        )
                    ),

                    # ------------------------------------------------
                    # R00 - BIT 2
                    # État de la zone
                    # ------------------------------------------------
                    "state": (
                        self.client.read_zone_state(
                            base_address,
                            slave=self.slave,
                        )
                    ),

                    # ------------------------------------------------
                    # R00 - BITS 4-5
                    # Vitesse
                    # ------------------------------------------------
                    "speed": (
                        self.client.read_zone_speed_name(
                            base_address,
                            slave=self.slave,
                        )
                    ),

                    # ------------------------------------------------
                    # R00 - BITS 6-7
                    # Mode veille
                    # ------------------------------------------------
                    "sleep_mode": (
                        self.client.read_zone_sleep_mode_name(
                            base_address,
                            slave=self.slave,
                        )
                    ),

                    # ------------------------------------------------
                    # R00 - BITS 8-11
                    # Mode
                    # ------------------------------------------------
                    "mode": (
                        self.client.read_zone_mode_name(
                            base_address,
                            slave=self.slave,
                        )
                    ),

                    # ------------------------------------------------
                    # R00 - BIT 12
                    # Mode automatique
                    # ------------------------------------------------
                    "automatic_mode": (
                        self.client.read_zone_automatic_mode(
                            base_address,
                            slave=self.slave,
                        )
                    ),

                    # ------------------------------------------------
                    # R00 - BIT 15
                    # Fonction dépendante du système
                    # ------------------------------------------------
                    "bit15": (
                        self.client.read_zone_bit15(
                            base_address,
                            slave=self.slave,
                        )
                    ),

                    # ------------------------------------------------
                    # R03
                    # Consigne
                    # ------------------------------------------------
                    "setpoint": (
                        self.client.read_zone_setpoint(
                            base_address,
                            slave=self.slave,
                        )
                    ),

                    # ------------------------------------------------
                    # R08
                    # Température sonde
                    # ------------------------------------------------
                    "temperature": (
                        self.client.read_zone_temperature(
                            base_address,
                            slave=self.slave,
                        )
                    ),

                    # ------------------------------------------------
                    # R10
                    # Température thermostat
                    # ------------------------------------------------
                    "thermostat_temperature": (
                        self.client.read_zone_thermostat_temperature(
                            base_address,
                            slave=self.slave,
                        )
                    ),

                    # ------------------------------------------------
                    # R14-R19
                    # Nom Airzone
                    # ------------------------------------------------
                    "name": (
                        self.client.read_zone_name(
                            base_address,
                            slave=self.slave,
                        )
                    ),

                    # ------------------------------------------------
                    # R26 - BITS 0-2
                    # Offset thermostat Lite
                    # ------------------------------------------------
                    "thermostat_offset": (
                        self.client.read_thermostat_lite_setpoint_offset(
                            base_address,
                            slave=self.slave,
                        )
                    ),

                    # ------------------------------------------------
                    # R26 - BIT 3
                    # LED thermostat
                    # ------------------------------------------------
                    "thermostat_led": (
                        self.client.read_thermostat_lite_status_led(
                            base_address,
                            slave=self.slave,
                        )
                    ),

                    # ------------------------------------------------
                    # R26 - BIT 5
                    # Thermostat Lite présent
                    # ------------------------------------------------
                    "thermostat_lite_present": (
                        self.client.read_thermostat_lite_present(
                            base_address,
                            slave=self.slave,
                        )
                    ),

                    # ------------------------------------------------
                    # R31
                    # Humidité
                    # ------------------------------------------------
                    "humidity": (
                        self.client.read_zone_humidity(
                            base_address,
                            slave=self.slave,
                        )
                    ),
                }

            return {
                "machine": {
                    "mode_name": machine_mode,
                    "speed_name": machine_speed,
                },
                "zones": zones,
                "zone_data": zone_data,
            }

        finally:
            self.client.close()
