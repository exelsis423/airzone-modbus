"""Sensors for Airzone Modbus."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
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

    entities = [
        AirzoneMachineMode(coordinator, entry),
        AirzoneMachineSpeed(coordinator, entry),
    ]

    for zone in coordinator.data["zones"]:
        entities.extend(
            [
                AirzoneZoneSpeed(
                    coordinator,
                    entry,
                    zone,
                ),
                AirzoneZoneSleepMode(
                    coordinator,
                    entry,
                    zone,
                ),
                AirzoneZoneMode(
                    coordinator,
                    entry,
                    zone,
                ),
                AirzoneZoneSetpoint(
                    coordinator,
                    entry,
                    zone,
                ),
                AirzoneZoneTemperature(
                    coordinator,
                    entry,
                    zone,
                ),
                AirzoneZoneThermostatTemperature(
                    coordinator,
                    entry,
                    zone,
                ),
            ]
        )

    async_add_entities(entities)


class AirzoneMachineMode(
    CoordinatorEntity[AirzoneCoordinator],
    SensorEntity,
):
    """Machine operating mode."""

    _attr_icon = "mdi:air-conditioner"

    def __init__(
        self,
        coordinator: AirzoneCoordinator,
        entry: ConfigEntry,
    ) -> None:
        super().__init__(coordinator)

        self._attr_unique_id = (
            f"{entry.entry_id}_machine_mode"
        )
        self._attr_name = "Airzone — Mode"

    @property
    def native_value(self) -> str:
        """Return the machine mode."""

        return self.coordinator.data["machine"]["mode_name"]


class AirzoneMachineSpeed(
    CoordinatorEntity[AirzoneCoordinator],
    SensorEntity,
):
    """Machine fan speed."""

    _attr_icon = "mdi:fan"

    def __init__(
        self,
        coordinator: AirzoneCoordinator,
        entry: ConfigEntry,
    ) -> None:
        super().__init__(coordinator)

        self._attr_unique_id = (
            f"{entry.entry_id}_machine_speed"
        )
        self._attr_name = (
            "Airzone — Vitesse ventilation"
        )

    @property
    def native_value(self) -> str:
        """Return the machine fan speed."""

        return self.coordinator.data["machine"]["speed_name"]


class AirzoneZoneSpeed(
    CoordinatorEntity[AirzoneCoordinator],
    SensorEntity,
):
    """Fan speed of an Airzone zone."""

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
    def native_value(self) -> str:
        """Return the zone fan speed."""

        return self.coordinator.data["zone_data"][
            self.zone
        ]["speed"]


class AirzoneZoneSleepMode(
    CoordinatorEntity[AirzoneCoordinator],
    SensorEntity,
):
    """Sleep mode of an Airzone zone."""

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
    def native_value(self) -> str:
        """Return the zone sleep mode."""

        return self.coordinator.data["zone_data"][
            self.zone
        ]["sleep_mode"]


class AirzoneZoneMode(
    CoordinatorEntity[AirzoneCoordinator],
    SensorEntity,
):
    """Operating mode of an Airzone zone."""

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
    def native_value(self) -> str:
        """Return the zone operating mode."""

        return self.coordinator.data["zone_data"][
            self.zone
        ]["mode"]


class AirzoneZoneSetpoint(
    CoordinatorEntity[AirzoneCoordinator],
    SensorEntity,
):
    """Setpoint of an Airzone zone."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_icon = "mdi:thermometer"

    def __init__(
        self,
        coordinator: AirzoneCoordinator,
        entry: ConfigEntry,
        zone: int,
    ) -> None:
        super().__init__(coordinator)

        self.zone = zone

        self._attr_unique_id = (
            f"{entry.entry_id}_zone_{zone}_setpoint"
        )
        self._attr_name = (
            f"Airzone — Zone {zone} — Consigne"
        )

    @property
    def native_value(self) -> float:
        """Return the zone setpoint."""

        return self.coordinator.data["zone_data"][
            self.zone
        ]["setpoint"]


class AirzoneZoneTemperature(
    CoordinatorEntity[AirzoneCoordinator],
    SensorEntity,
):
    """Current temperature measured by the zone sensor."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_icon = "mdi:thermometer"

    def __init__(
        self,
        coordinator: AirzoneCoordinator,
        entry: ConfigEntry,
        zone: int,
    ) -> None:
        super().__init__(coordinator)

        self.zone = zone

        self._attr_unique_id = (
            f"{entry.entry_id}_zone_{zone}_temperature"
        )
        self._attr_name = (
            f"Airzone — Zone {zone} — Température sonde"
        )

    @property
    def native_value(self) -> float:
        """Return the zone temperature."""

        return self.coordinator.data["zone_data"][
            self.zone
        ]["temperature"]


class AirzoneZoneThermostatTemperature(
    CoordinatorEntity[AirzoneCoordinator],
    SensorEntity,
):
    """Temperature measured by the zone thermostat."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_icon = "mdi:thermometer"

    def __init__(
        self,
        coordinator: AirzoneCoordinator,
        entry: ConfigEntry,
        zone: int,
    ) -> None:
        super().__init__(coordinator)

        self.zone = zone

        self._attr_unique_id = (
            f"{entry.entry_id}_zone_{zone}_thermostat_temperature"
        )
        self._attr_name = (
            f"Airzone — Zone {zone} — Température thermostat"
        )

    @property
    def native_value(self) -> float:
        """Return the thermostat temperature."""

        return self.coordinator.data["zone_data"][
            self.zone
        ]["thermostat_temperature"]
