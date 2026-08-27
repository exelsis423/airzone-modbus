"""Sensors for Airzone Modbus."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
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
    """Set up Airzone Modbus sensors."""

    coordinator: AirzoneCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            AirzoneMachineModeSensor(coordinator, entry),
            AirzoneMachineSpeedSensor(coordinator, entry),
            AirzoneMachineZonesSensor(coordinator, entry),
        ]
    )


class AirzoneMachineModeSensor(
    CoordinatorEntity[AirzoneCoordinator],
    SensorEntity,
):
    """Sensor for the Airzone machine operating mode."""

    _attr_name = "Airzone — Mode"
    _attr_icon = "mdi:air-conditioner"

    def __init__(
        self,
        coordinator: AirzoneCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""

        super().__init__(coordinator)

        self._attr_unique_id = (
            f"{entry.entry_id}_machine_mode"
        )

    @property
    def native_value(self) -> str:
        """Return the current operating mode."""

        return self.coordinator.data["machine"]["mode_name"]


class AirzoneMachineSpeedSensor(
    CoordinatorEntity[AirzoneCoordinator],
    SensorEntity,
):
    """Sensor for the Airzone machine fan speed."""

    _attr_name = "Airzone — Vitesse ventilation"
    _attr_icon = "mdi:fan"

    def __init__(
        self,
        coordinator: AirzoneCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""

        super().__init__(coordinator)

        self._attr_unique_id = (
            f"{entry.entry_id}_machine_fan_speed"
        )

    @property
    def native_value(self) -> str:
        """Return the current fan speed."""

        return self.coordinator.data["machine"]["speed_name"]


class AirzoneMachineZonesSensor(
    CoordinatorEntity[AirzoneCoordinator],
    SensorEntity,
):
    """Sensor for the number of Airzone zones."""

    _attr_name = "Airzone — Zones présentes"
    _attr_icon = "mdi:home-group"

    def __init__(
        self,
        coordinator: AirzoneCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""

        super().__init__(coordinator)

        self._attr_unique_id = (
            f"{entry.entry_id}_machine_zones"
        )

    @property
    def native_value(self) -> int:
        """Return the number of zones."""

        return len(self.coordinator.data["zones"])

    @property
    def extra_state_attributes(self) -> dict:
        """Return the list of present zones."""

        return {
            "zones": self.coordinator.data["zones"],
        }
