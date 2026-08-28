"""Number entities for Airzone Modbus."""

from __future__ import annotations

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
)
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
    """Set up Airzone Modbus number entities."""

    coordinator: AirzoneCoordinator = hass.data[
        DOMAIN
    ][entry.entry_id]

    entities = []

    for zone in coordinator.data["zones"]:
        entities.append(
            AirzoneZoneThermostatOffsetNumber(
                coordinator,
                entry,
                zone,
            )
        )

        entities.append(
            AirzoneZoneSetpointNumber(
                coordinator,
                entry,
                zone,
            )
        )

    async_add_entities(entities)


class AirzoneZoneThermostatOffsetNumber(
    CoordinatorEntity[AirzoneCoordinator],
    NumberEntity,
):
    """Offset température du thermostat Lite."""

    _attr_device_class = NumberDeviceClass.TEMPERATURE
    _attr_native_min_value = -3
    _attr_native_max_value = 3
    _attr_native_step = 1
    _attr_native_unit_of_measurement = "°C"
    _attr_icon = "mdi:thermometer-plus-minus"

    def __init__(
        self,
        coordinator: AirzoneCoordinator,
        entry: ConfigEntry,
        zone: int,
    ) -> None:
        super().__init__(coordinator)

        self.zone = zone

        self._attr_unique_id = (
            f"{entry.entry_id}_zone_{zone}_thermostat_offset_number"
        )

        self._attr_name = (
            f"Airzone — Zone {zone} — "
            "Offset thermostat"
        )

    @property
    def native_value(self) -> float | None:
        """Retourne l'offset actuel."""

        return self.coordinator.data[
            "zone_data"
        ][self.zone]["thermostat_offset"]

    async def async_set_native_value(
        self,
        value: float,
    ) -> None:
        """Modifie l'offset du thermostat."""

        await self.coordinator.async_write_zone_thermostat_offset(
            self.zone,
            int(value),
        )

class AirzoneZoneSetpointNumber(
    CoordinatorEntity[AirzoneCoordinator],
    NumberEntity,
):
    """Consigne de température de la zone."""

    _attr_device_class = NumberDeviceClass.TEMPERATURE
    _attr_native_min_value = 18
    _attr_native_max_value = 30
    _attr_native_step = 0.5
    _attr_native_unit_of_measurement = "°C"
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
            f"{entry.entry_id}_zone_{zone}_setpoint_number"
        )

        self._attr_name = (
            f"Airzone — Zone {zone} — "
            "Consigne"
        )

    @property
    def native_value(self) -> float | None:
        """Retourne la consigne actuelle."""

        return self.coordinator.data[
            "zone_data"
        ][self.zone]["setpoint"]

    async def async_set_native_value(
        self,
        value: float,
    ) -> None:
        """Modifie la consigne."""

        await self.coordinator.async_write_zone_setpoint(
            self.zone,
            value,
        )
