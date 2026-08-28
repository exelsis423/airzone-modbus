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

    # ================================================================
    # LECTURE
    # ================================================================

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

            machine_mode = self.client.read_machine_mode(
                slave=self.slave,
            )

            machine_mode_name = self.client.read_machine_mode_name(
                slave=self.slave,
            )

            machine_speed = self.client.read_machine_speed(
                slave=self.slave,
            )

            machine_speed_name = self.client.read_machine_speed_name(
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
                    "mode": machine_mode,
                    "mode_name": machine_mode_name,
                    "speed": machine_speed,
                    "speed_name": machine_speed_name,
                },
                "zones": zones,
                "zone_data": zone_data,
            }

        finally:
            self.client.close()

    # ================================================================
    # ÉCRITURES MACHINE
    # ================================================================

    async def async_write_machine_mode(
        self,
        mode: int,
    ) -> None:
        """Écrit le mode machine."""

        await self.hass.async_add_executor_job(
            self._write_machine_mode,
            mode,
        )

        if self.data is not None:
            self.data["machine"]["mode"] = mode

            mode_names = {
                0: "Arrêt",
                1: "Refroidissement",
                2: "Chauffage rayonnant",
                3: "Ventilation",
                4: "Chauffage air",
                5: "Chauffage",
                6: "Sec",
                7: "Chaud auxiliaire",
                8: "Refroidissement rayonnant",
                9: "Refroidissement",
                258: "Chauffage",
            }

            self.data["machine"]["mode_name"] = mode_names.get(
                mode,
                f"Inconnu ({mode})",
            )

            self.async_set_updated_data(self.data)

    def _write_machine_mode(
        self,
        mode: int,
    ) -> None:
        """Écriture synchrone du mode machine."""

        if not self.client.connect():
            raise RuntimeError(
                "Impossible de se connecter à Airzone"
            )

        try:
            self.client.write_machine_mode(
                mode,
                slave=self.slave,
            )
        finally:
            self.client.close()

    async def async_write_machine_speed(
        self,
        speed: int,
    ) -> None:
        """Écrit la vitesse machine."""

        await self.hass.async_add_executor_job(
            self._write_machine_speed,
            speed,
        )

        if self.data is not None:
            self.data["machine"]["speed"] = speed

            speed_names = {
                0: "Automatique",
                1: "Faible",
                2: "Moyenne",
                3: "Élevée",
            }

            self.data["machine"]["speed_name"] = speed_names.get(
                speed,
                f"Inconnu ({speed})",
            )

            self.async_set_updated_data(self.data)

    def _write_machine_speed(
        self,
        speed: int,
    ) -> None:
        """Écriture synchrone de la vitesse machine."""

        if not self.client.connect():
            raise RuntimeError(
                "Impossible de se connecter à Airzone"
            )

        try:
            self.client.write_machine_speed(
                speed,
                slave=self.slave,
            )
        finally:
            self.client.close()

    # ================================================================
    # ÉCRITURES ZONES - R00
    # ================================================================

    async def async_write_zone_mode(
        self,
        zone: int,
        mode: int,
    ) -> None:
        """Écrit le mode d'une zone."""

        await self.hass.async_add_executor_job(
            self._write_zone_mode,
            zone,
            mode,
        )

        if self.data is not None:
            mode_names = {
                0: "Arrêt",
                1: "Refroidissement",
                3: "Ventilation",
                5: "Chauffage",
                6: "Sec",
            }

            self.data["zone_data"][zone]["mode"] = mode_names.get(
                mode,
                f"Inconnu ({mode})",
            )

            self.async_set_updated_data(self.data)

    def _write_zone_mode(
        self,
        zone: int,
        mode: int,
    ) -> None:
        """Écriture synchrone du mode d'une zone."""

        if not self.client.connect():
            raise RuntimeError(
                "Impossible de se connecter à Airzone"
            )

        try:
            base_address = zone * 256

            self.client.write_zone_mode(
                base_address,
                mode,
                slave=self.slave,
            )
        finally:
            self.client.close()

    async def async_write_zone_state(
        self,
        zone: int,
        state: bool,
    ) -> None:
        """Active ou désactive une zone."""

        await self.hass.async_add_executor_job(
            self._write_zone_state,
            zone,
            state,
        )

        if self.data is not None:
            self.data["zone_data"][zone]["state"] = state

            self.async_set_updated_data(self.data)

    def _write_zone_state(
        self,
        zone: int,
        state: bool,
    ) -> None:
        """Écriture synchrone de l'état d'une zone."""

        if not self.client.connect():
            raise RuntimeError(
                "Impossible de se connecter à Airzone"
            )

        try:
            base_address = zone * 256

            self.client.write_zone_state(
                base_address,
                state,
                slave=self.slave,
            )
        finally:
            self.client.close()

    async def async_write_zone_automatic_mode(
        self,
        zone: int,
        enabled: bool,
    ) -> None:
        """Active ou désactive le mode automatique."""

        await self.hass.async_add_executor_job(
            self._write_zone_automatic_mode,
            zone,
            enabled,
        )

        if self.data is not None:
            self.data["zone_data"][zone][
                "automatic_mode"
            ] = enabled

            self.async_set_updated_data(self.data)

    def _write_zone_automatic_mode(
        self,
        zone: int,
        enabled: bool,
    ) -> None:
        """Écriture synchrone du mode automatique."""

        if not self.client.connect():
            raise RuntimeError(
                "Impossible de se connecter à Airzone"
            )

        try:
            base_address = zone * 256

            self.client.write_zone_automatic_mode(
                base_address,
                enabled,
                slave=self.slave,
            )
        finally:
            self.client.close()

    async def async_write_zone_sleep_mode(
        self,
        zone: int,
        sleep_mode: int,
    ) -> None:
        """Écrit le mode veille d'une zone."""

        await self.hass.async_add_executor_job(
            self._write_zone_sleep_mode,
            zone,
            sleep_mode,
        )

        if self.data is not None:
            sleep_mode_names = {
                0: "Veille Off",
                1: "Veille 30",
                2: "Veille 60",
                3: "Veille 90",
            }

            self.data["zone_data"][zone][
                "sleep_mode"
            ] = sleep_mode_names.get(
                sleep_mode,
                f"Inconnu ({sleep_mode})",
            )

            self.async_set_updated_data(self.data)

    def _write_zone_sleep_mode(
        self,
        zone: int,
        sleep_mode: int,
    ) -> None:
        """Écriture synchrone du mode veille."""

        if not self.client.connect():
            raise RuntimeError(
                "Impossible de se connecter à Airzone"
            )

        try:
            base_address = zone * 256

            self.client.write_zone_sleep_mode(
                base_address,
                sleep_mode,
                slave=self.slave,
            )
        finally:
            self.client.close()

    async def async_write_zone_schedule_disabled(
        self,
        zone: int,
        disabled: bool,
    ) -> None:
        """Active ou désactive les programmations horaires."""

        await self.hass.async_add_executor_job(
            self._write_zone_schedule_disabled,
            zone,
            disabled,
        )

        if self.data is not None:
            self.data["zone_data"][zone][
                "schedule_disabled"
            ] = disabled

            self.async_set_updated_data(self.data)

    def _write_zone_schedule_disabled(
        self,
        zone: int,
        disabled: bool,
    ) -> None:
        """Écriture synchrone de la programmation horaire."""

        if not self.client.connect():
            raise RuntimeError(
                "Impossible de modifier la programmation horaire"
            )

        try:
            base_address = zone * 256

            self.client.write_zone_schedule_disabled(
                base_address,
                disabled,
                slave=self.slave,
            )
        finally:
            self.client.close()

    async def async_write_zone_speed(
        self,
        zone: int,
        speed: int,
    ) -> None:
        """Écrit la vitesse d'une zone."""

        await self.hass.async_add_executor_job(
            self._write_zone_speed,
            zone,
            speed,
        )

        if self.data is not None:
            speed_names = {
                0: "Automatique",
                1: "Faible",
                2: "Moyenne",
                3: "Élevée",
            }

            self.data["zone_data"][zone]["speed"] = speed_names.get(
                speed,
                f"Inconnu ({speed})",
            )

            self.async_set_updated_data(self.data)

    def _write_zone_speed(
        self,
        zone: int,
        speed: int,
    ) -> None:
        """Écriture synchrone de la vitesse d'une zone."""

        if not self.client.connect():
            raise RuntimeError(
                "Impossible de se connecter à Airzone"
            )

        try:
            base_address = zone * 256

            self.client.write_zone_speed(
                base_address,
                speed,
                slave=self.slave,
            )
        finally:
            self.client.close()
