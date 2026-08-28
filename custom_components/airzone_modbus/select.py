"""Select entities for Airzone Modbus."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import AirzoneCoordinator


# ============================================================
# MACHINE
# ============================================================

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
    9: "Chauffage",
    258: "Chauffage",
}

MACHINE_SPEEDS = {
    0: "Automatique",
    1: "Faible",
    2: "Moyenne",
    3: "Élevée",
}


# ============================================================
# ZONE - R00
# ============================================================

ZONE_MODES = {
    0: "Arrêt",
    1: "Refroidissement",
    3: "Ventilation",
    5: "Chauffage",
    6: "Sec",
}

ZONE_SPEEDS = {
    0: "Automatique",
    1: "Faible",
    2: "Moyenne",
    3: "Élevée",
}

ZONE_SLEEP_MODES = {
    0: "Veille Off",
    1: "Veille 30",
    2: "Veille 60",
    3: "Veille 90",
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Configure les selects Airzone."""

    coordinator: AirzoneCoordinator = hass.data[
        DOMAIN
    ][entry.entry_id]

    entities = [
        # --------------------------------------------------------
        # MACHINE
        # --------------------------------------------------------
        AirzoneMachineModeSelect(
            coordinator,
            entry,
        ),
        AirzoneMachineSpeedSelect(
            coordinator,
            entry,
        ),
    ]

    # ------------------------------------------------------------
    # ZONES
    # ------------------------------------------------------------

    for zone in coordinator.data["zones"]:
        entities.extend(
            [
                AirzoneZoneModeSelect(
                    coordinator,
                    entry,
                    zone,
                ),
                AirzoneZoneSpeedSelect(
                    coordinator,
                    entry,
                    zone,
                ),
                AirzoneZoneSleepModeSelect(
                    coordinator,
                    entry,
                    zone,
                ),
            ]
        )

    async_add_entities(entities)


# ============================================================
# MACHINE - MODE
# ============================================================


class AirzoneMachineModeSelect(
    CoordinatorEntity[AirzoneCoordinator],
    SelectEntity,
):
    """Sélecteur du mode machine."""

    _attr_has_entity_name = False
    _attr_name = "Airzone — Mode"
    _attr_icon = "mdi:air-conditioner"

    def __init__(
        self,
        coordinator: AirzoneCoordinator,
        entry: ConfigEntry,
    ) -> None:
        super().__init__(coordinator)

        self._entry = entry
        self._attr_unique_id = (
            f"{entry.entry_id}_machine_mode"
        )

    @property
    def options(self) -> list[str]:
        """Retourne les modes disponibles."""
        return list(MACHINE_MODES.values())

    @property
    def current_option(self) -> str | None:
        """Retourne le mode actuel."""

        if not self.coordinator.data:
            return None

        mode = self.coordinator.data[
            "machine"
        ]["mode"]

        return MACHINE_MODES.get(mode)

    async def async_select_option(
        self,
        option: str,
    ) -> None:
        """Change le mode machine."""

        mode = next(
            value
            for value, name in MACHINE_MODES.items()
            if name == option
        )

        await self.coordinator.async_write_machine_mode(
            mode
        )


# ============================================================
# MACHINE - VITESSE
# ============================================================


class AirzoneMachineSpeedSelect(
    CoordinatorEntity[AirzoneCoordinator],
    SelectEntity,
):
    """Sélecteur de la vitesse machine."""

    _attr_has_entity_name = False
    _attr_name = "Airzone — Vitesse ventilation"
    _attr_icon = "mdi:fan"

    def __init__(
        self,
        coordinator: AirzoneCoordinator,
        entry: ConfigEntry,
    ) -> None:
        super().__init__(coordinator)

        self._entry = entry
        self._attr_unique_id = (
            f"{entry.entry_id}_machine_speed"
        )

    @property
    def options(self) -> list[str]:
        """Retourne les vitesses disponibles."""
        return list(MACHINE_SPEEDS.values())

    @property
    def current_option(self) -> str | None:
        """Retourne la vitesse actuelle."""

        if not self.coordinator.data:
            return None

        speed = self.coordinator.data[
            "machine"
        ]["speed"]

        return MACHINE_SPEEDS.get(speed)

    async def async_select_option(
        self,
        option: str,
    ) -> None:
        """Change la vitesse machine."""

        speed = next(
            value
            for value, name in MACHINE_SPEEDS.items()
            if name == option
        )

        await self.coordinator.async_write_machine_speed(
            speed
        )


# ============================================================
# ZONE - MODE
# R00 bits 8-11
# ============================================================


class AirzoneZoneModeSelect(
    CoordinatorEntity[AirzoneCoordinator],
    SelectEntity,
):
    """Sélecteur du mode d'une zone."""

    _attr_has_entity_name = False
    _attr_icon = "mdi:thermostat"

    def __init__(
        self,
        coordinator: AirzoneCoordinator,
        entry: ConfigEntry,
        zone: int,
    ) -> None:
        super().__init__(coordinator)

        self.zone = zone

        self._attr_unique_id = (
            f"{entry.entry_id}_zone_{zone}_mode"
        )

        self._attr_name = (
            f"Airzone — Zone {zone} — Mode"
        )

    @property
    def options(self) -> list[str]:
        """Retourne les modes disponibles."""
        return list(ZONE_MODES.values())

    @property
    def current_option(self) -> str | None:
        """Retourne le mode actuel."""

        if not self.coordinator.data:
            return None

        mode = self.coordinator.data[
            "zone_data"
        ][self.zone]["mode"]

        return mode

    async def async_select_option(
        self,
        option: str,
    ) -> None:
        """Change le mode de la zone."""

        mode = next(
            value
            for value, name in ZONE_MODES.items()
            if name == option
        )

        await self.coordinator.async_write_zone_mode(
            self.zone,
            mode,
        )


# ============================================================
# ZONE - VITESSE
# R00 bits 4-5
# ============================================================


class AirzoneZoneSpeedSelect(
    CoordinatorEntity[AirzoneCoordinator],
    SelectEntity,
):
    """Sélecteur de la vitesse d'une zone."""

    _attr_has_entity_name = False
    _attr_icon = "mdi:fan"

    def __init__(
        self,
        coordinator: AirzoneCoordinator,
        entry: ConfigEntry,
        zone: int,
    ) -> None:
        super().__init__(coordinator)

        self.zone = zone

        self._attr_unique_id = (
            f"{entry.entry_id}_zone_{zone}_speed"
        )

        self._attr_name = (
            f"Airzone — Zone {zone} — Vitesse"
        )

    @property
    def options(self) -> list[str]:
        """Retourne les vitesses disponibles."""
        return list(ZONE_SPEEDS.values())

    @property
    def current_option(self) -> str | None:
        """Retourne la vitesse actuelle."""

        if not self.coordinator.data:
            return None

        speed = self.coordinator.data[
            "zone_data"
        ][self.zone]["speed"]

        return speed

    async def async_select_option(
        self,
        option: str,
    ) -> None:
        """Change la vitesse de la zone."""

        speed = next(
            value
            for value, name in ZONE_SPEEDS.items()
            if name == option
        )

        await self.coordinator.async_write_zone_speed(
            self.zone,
            speed,
        )


# ============================================================
# ZONE - MODE VEILLE
# R00 bits 6-7
# ============================================================


class AirzoneZoneSleepModeSelect(
    CoordinatorEntity[AirzoneCoordinator],
    SelectEntity,
):
    """Sélecteur du mode veille d'une zone."""

    _attr_has_entity_name = False
    _attr_icon = "mdi:sleep"

    def __init__(
        self,
        coordinator: AirzoneCoordinator,
        entry: ConfigEntry,
        zone: int,
    ) -> None:
        super().__init__(coordinator)

        self.zone = zone

        self._attr_unique_id = (
            f"{entry.entry_id}_zone_{zone}_sleep_mode"
        )

        self._attr_name = (
            f"Airzone — Zone {zone} — Mode veille"
        )

    @property
    def options(self) -> list[str]:
        """Retourne les modes veille disponibles."""
        return list(ZONE_SLEEP_MODES.values())

    @property
    def current_option(self) -> str | None:
        """Retourne le mode veille actuel."""

        if not self.coordinator.data:
            return None

        sleep_mode = self.coordinator.data[
            "zone_data"
        ][self.zone]["sleep_mode"]

        return sleep_mode

    async def async_select_option(
        self,
        option: str,
    ) -> None:
        """Change le mode veille de la zone."""

        sleep_mode = next(
            value
            for value, name in ZONE_SLEEP_MODES.items()
            if name == option
        )

        await self.coordinator.async_write_zone_sleep_mode(
            self.zone,
            sleep_mode,
        )
