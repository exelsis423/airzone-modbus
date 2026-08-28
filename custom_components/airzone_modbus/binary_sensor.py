"""Binary sensors for Airzone Modbus."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .const import DOMAIN
from .coordinator import AirzoneCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Airzone Modbus binary sensors."""

    coordinator: AirzoneCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []

    for zone in coordinator.data["zones"]:
        entities.extend(
            [
                AirzoneZoneLocalVentilation(
                    coordinator,
                    entry,
                    zone,
                ),
                AirzoneZoneScheduleDisabled(
                    coordinator,
                    entry,
                    zone,
                ),
                AirzoneZoneState(
                    coordinator,
                    entry,
                    zone,
                ),
            ]
        )

    async_add_entities(entities)


class AirzoneZoneLocalVentilation(
    CoordinatorEntity[AirzoneCoordinator],
    BinarySensorEntity,
):
    """Local ventilation state of an Airzone zone."""

    _attr_icon = "mdi:fan"

    def __init__(
        self,
        coordinator: AirzoneCoordinator,
        entry: ConfigEntry,
        zone: int,
    ) -> None:
        """Initialize the binary sensor."""

        super().__init__(coordinator)

        self.zone = zone

        self._attr_unique_id = (
            f"{entry.entry_id}_zone_{zone}_local_ventilation"
        )

        self._attr_name = (
            f"Airzone — Zone {zone} — Ventilation locale"
        )

    @property
    def is_on(self) -> bool:
        """Return the local ventilation state."""

        return self.coordinator.data["zone_data"][
            self.zone
        ]["local_ventilation"]


class AirzoneZoneScheduleDisabled(
    CoordinatorEntity[AirzoneCoordinator],
    BinarySensorEntity,
):
    """Schedule disabled state of an Airzone zone."""

    _attr_icon = "mdi:calendar-remove"

    def __init__(
        self,
        coordinator: AirzoneCoordinator,
        entry: ConfigEntry,
        zone: int,
    ) -> None:
        """Initialize the binary sensor."""

        super().__init__(coordinator)

        self.zone = zone

        self._attr_unique_id = (
            f"{entry.entry_id}_zone_{zone}_schedule_disabled"
        )

        self._attr_name = (
            f"Airzone — Zone {zone} — Programmation désactivée"
        )

    @property
    def is_on(self) -> bool:
        """Return whether the schedule is disabled."""

        return self.coordinator.data["zone_data"][
            self.zone
        ]["schedule_disabled"]


class AirzoneZoneState(
    CoordinatorEntity[AirzoneCoordinator],
    BinarySensorEntity,
):
    """State of an Airzone zone."""

    _attr_icon = "mdi:power"

    def __init__(
        self,
        coordinator: AirzoneCoordinator,
        entry: ConfigEntry,
        zone: int,
    ) -> None:
        """Initialize the binary sensor."""

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
        """Return the zone state."""

        return self.coordinator.data["zone_data"][
            self.zone
        ]["state"]
