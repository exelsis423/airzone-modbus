"""Switch entities for Airzone Modbus."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import AirzoneCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Configure les switches des zones."""

    coordinator: AirzoneCoordinator = hass.data[
        DOMAIN
    ][entry.entry_id]

    entities = []

    for zone in coordinator.data["zones"]:
        entities.extend(
            [
                AirzoneZoneStateSwitch(
                    coordinator,
                    entry,
                    zone,
                ),
                AirzoneZoneAutomaticModeSwitch(
                    coordinator,
                    entry,
                    zone,
                ),
                AirzoneZoneScheduleSwitch(
                    coordinator,
                    entry,
                    zone,
                ),
            ]
        )

    async_add_entities(entities)


# ============================================================
# ZONE - R00 BIT 2
# État de la zone
# ============================================================


class AirzoneZoneStateSwitch(
    CoordinatorEntity[AirzoneCoordinator],
    SwitchEntity,
):
    """Interrupteur marche/arrêt de la zone."""

    _attr_icon = "mdi:power"

    def __init__(
        self,
        coordinator: AirzoneCoordinator,
        entry: ConfigEntry,
        zone: int,
    ) -> None:
        super().__init__(coordinator)

        self.zone = zone

        self._attr_unique_id = (
            f"{entry.entry_id}_zone_{zone}_state"
        )

        self._attr_name = (
            f"Airzone — Zone {zone} — État"
        )

    @property
    def is_on(self) -> bool:
        """Retourne l'état de la zone."""

        return self.coordinator.data[
            "zone_data"
        ][self.zone]["state"]

    async def async_turn_on(self, **kwargs) -> None:
        """Allume la zone."""

        await self.coordinator.async_write_zone_state(
            self.zone,
            True,
        )

    async def async_turn_off(self, **kwargs) -> None:
        """Éteint la zone."""

        await self.coordinator.async_write_zone_state(
            self.zone,
            False,
        )


# ============================================================
# ZONE - R00 BIT 12
# Mode automatique
# ============================================================


class AirzoneZoneAutomaticModeSwitch(
    CoordinatorEntity[AirzoneCoordinator],
    SwitchEntity,
):
    """Interrupteur du mode automatique."""

    _attr_icon = "mdi:auto-mode"

    def __init__(
        self,
        coordinator: AirzoneCoordinator,
        entry: ConfigEntry,
        zone: int,
    ) -> None:
        super().__init__(coordinator)

        self.zone = zone

        self._attr_unique_id = (
            f"{entry.entry_id}_zone_{zone}_automatic_mode"
        )

        self._attr_name = (
            f"Airzone — Zone {zone} — Mode automatique"
        )

    @property
    def is_on(self) -> bool:
        """Retourne l'état du mode automatique."""

        return self.coordinator.data[
            "zone_data"
        ][self.zone]["automatic_mode"]

    async def async_turn_on(self, **kwargs) -> None:
        """Active le mode automatique."""

        await self.coordinator.async_write_zone_automatic_mode(
            self.zone,
            True,
        )

    async def async_turn_off(self, **kwargs) -> None:
        """Désactive le mode automatique."""

        await self.coordinator.async_write_zone_automatic_mode(
            self.zone,
            False,
        )


# ============================================================
# ZONE - R00 BIT 1
# Programmation horaire
# ============================================================


class AirzoneZoneScheduleSwitch(
    CoordinatorEntity[AirzoneCoordinator],
    SwitchEntity,
):
    """Interrupteur des programmations horaires."""

    _attr_icon = "mdi:calendar-clock"

    def __init__(
        self,
        coordinator: AirzoneCoordinator,
        entry: ConfigEntry,
        zone: int,
    ) -> None:
        super().__init__(coordinator)

        self.zone = zone

        self._attr_unique_id = (
            f"{entry.entry_id}_zone_{zone}_schedule"
        )

        self._attr_name = (
            f"Airzone — Zone {zone} — "
            "Programmation horaire"
        )

    @property
    def is_on(self) -> bool:
        """Retourne l'état des programmations horaires."""

        # Le registre indique :
        # 0 = programmations activées
        # 1 = programmations désactivées
        return not self.coordinator.data[
            "zone_data"
        ][self.zone]["schedule_disabled"]

    async def async_turn_on(self, **kwargs) -> None:
        """Active les programmations horaires."""

        await self.coordinator.async_write_zone_schedule_disabled(
            self.zone,
            False,
        )

    async def async_turn_off(self, **kwargs) -> None:
        """Désactive les programmations horaires."""

        await self.coordinator.async_write_zone_schedule_disabled(
            self.zone,
            True,
        )
