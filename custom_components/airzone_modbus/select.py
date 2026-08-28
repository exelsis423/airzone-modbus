"""Select entities for Airzone Modbus."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import AirzoneCoordinator


MACHINE_MODES = {
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

MACHINE_SPEEDS = {
    0: "Automatique",
    1: "Faible",
    2: "Moyenne",
    3: "Élevée",
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Configure les selects machine."""

    coordinator: AirzoneCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            AirzoneMachineModeSelect(coordinator, entry),
            AirzoneMachineSpeedSelect(coordinator, entry),
        ]
    )


class AirzoneMachineModeSelect(
    CoordinatorEntity[AirzoneCoordinator],
    SelectEntity,
):
    """Sélecteur du mode machine."""

    _attr_has_entity_name = True
    _attr_name = "Mode"
    _attr_icon = "mdi:air-conditioner"

    def __init__(
        self,
        coordinator: AirzoneCoordinator,
        entry: ConfigEntry,
    ) -> None:
        super().__init__(coordinator)

        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_machine_mode"

    @property
    def options(self) -> list[str]:
        """Retourne les modes disponibles."""
        return list(MACHINE_MODES.values())

    @property
    def current_option(self) -> str | None:
        """Retourne le mode actuel."""
        if not self.coordinator.data:
            return None

        mode = self.coordinator.data["machine"]["mode"]

        return MACHINE_MODES.get(mode)

    async def async_select_option(self, option: str) -> None:
        """Change le mode machine."""

        mode = next(
            value
            for value, name in MACHINE_MODES.items()
            if name == option
        )

        await self.hass.async_add_executor_job(
            self._write_mode,
            mode,
        )

        await self.coordinator.async_request_refresh()

    def _write_mode(self, mode: int) -> None:
        """Écrit le mode dans le registre Modbus."""

        self.coordinator.client.connect()

        try:
            self.coordinator.client.write_machine_mode(
                mode,
                slave=self.coordinator.slave,
            )
        finally:
            self.coordinator.client.close()


class AirzoneMachineSpeedSelect(
    CoordinatorEntity[AirzoneCoordinator],
    SelectEntity,
):
    """Sélecteur de la vitesse machine."""

    _attr_has_entity_name = True
    _attr_name = "Vitesse ventilation"
    _attr_icon = "mdi:fan"

    def __init__(
        self,
        coordinator: AirzoneCoordinator,
        entry: ConfigEntry,
    ) -> None:
        super().__init__(coordinator)

        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_machine_speed"

    @property
    def options(self) -> list[str]:
        """Retourne les vitesses disponibles."""
        return list(MACHINE_SPEEDS.values())

    @property
    def current_option(self) -> str | None:
        """Retourne la vitesse actuelle."""
        if not self.coordinator.data:
            return None

        speed = self.coordinator.data.get("machine_speed")

        return MACHINE_SPEEDS.get(speed)

    async def async_select_option(self, option: str) -> None:
        """Change la vitesse machine."""

        speed = next(
            value
            for value, name in MACHINE_SPEEDS.items()
            if name == option
        )

        await self.hass.async_add_executor_job(
            self._write_speed,
            speed,
        )

        await self.coordinator.async_request_refresh()

    def _write_speed(self, speed: int) -> None:
        """Écrit la vitesse dans le registre Modbus."""

        self.coordinator.client.connect()

        try:
            self.coordinator.client.write_machine_speed(
                speed,
                slave=self.coordinator.slave,
            )
        finally:
            self.coordinator.client.close()
