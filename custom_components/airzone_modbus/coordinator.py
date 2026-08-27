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
    DOMAIN,
    UPDATE_INTERVAL,
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
    ) -> None:
        self.client = AirzoneClient(host, port)
        self.slave = slave

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
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
            zones = self.client.read_machine_zones(
                slave=self.slave,
            )

            return {
                "zones": zones,
            }

        finally:
            self.client.close()
