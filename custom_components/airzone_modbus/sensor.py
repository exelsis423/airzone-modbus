"""Sensors for Airzone Modbus."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfTemperature,
)
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

    coordinator: AirzoneCoordinator = hass.data[
        DOMAIN
    ][entry.entry_id]

    entities = []

    for zone in coordinator.data["zones"]:
        entities.extend(
            [
                # R03
                AirzoneZoneSetpoint(
                    coordinator,
                    entry,
                    zone,
                ),

                # R08
                AirzoneZoneTemperature(
                    coordinator,
                    entry,
                    zone,
                ),

                # R10
                AirzoneZoneThermostatTemperature(
                    coordinator,
                    entry,
                    zone,
                ),

                # R14-R19
                AirzoneZoneName(
                    coordinator,
                    entry,
                    zone,
                ),

                # R26 bits 0-2
                AirzoneZoneThermostatOffset(
                    coordinator,
                    entry,
                    zone,
                ),

                # R31
                AirzoneZoneHumidity(
                    coordinator,
                    entry,
                    zone,
                ),
            ]
        )

    async_add_entities(entities)


# ============================================================
# ZONE - R03
# ============================================================


class AirzoneZoneSetpoint(
    CoordinatorEntity[AirzoneCoordinator],
    SensorEntity,
):
    """Zone setpoint."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = (
        UnitOfTemperature.CELSIUS
    )
    _attr_icon = "mdi:thermometer"

    def __init__(
        self,
        coordinator,
        entry,
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
        return self.coordinator.data[
            "zone_data"
        ][self.zone]["setpoint"]


# ============================================================
# ZONE - R08
# ============================================================


class AirzoneZoneTemperature(
    CoordinatorEntity[AirzoneCoordinator],
    SensorEntity,
):
    """Zone sensor temperature."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = (
        UnitOfTemperature.CELSIUS
    )
    _attr_icon = "mdi:thermometer"

    def __init__(
        self,
        coordinator,
        entry,
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
        return self.coordinator.data[
            "zone_data"
        ][self.zone]["temperature"]


# ============================================================
# ZONE - R10
# ============================================================


class AirzoneZoneThermostatTemperature(
    CoordinatorEntity[AirzoneCoordinator],
    SensorEntity,
):
    """Zone thermostat temperature."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = (
        UnitOfTemperature.CELSIUS
    )
    _attr_icon = "mdi:thermometer"

    def __init__(
        self,
        coordinator,
        entry,
        zone: int,
    ) -> None:
        super().__init__(coordinator)

        self.zone = zone

        self._attr_unique_id = (
            f"{entry.entry_id}_zone_{zone}_thermostat_temperature"
        )

        self._attr_name = (
            f"Airzone — Zone {zone} — "
            "Température thermostat"
        )

    @property
    def native_value(self) -> float:
        """Return thermostat temperature."""
        return self.coordinator.data[
            "zone_data"
        ][self.zone]["thermostat_temperature"]


# ============================================================
# ZONE - R14-R19
# ============================================================


class AirzoneZoneName(
    CoordinatorEntity[AirzoneCoordinator],
    SensorEntity,
):
    """Airzone zone name."""

    _attr_icon = "mdi:rename-box"

    def __init__(
        self,
        coordinator,
        entry,
        zone: int,
    ) -> None:
        super().__init__(coordinator)

        self.zone = zone

        self._attr_unique_id = (
            f"{entry.entry_id}_zone_{zone}_name"
        )

        self._attr_name = (
            f"Airzone — Zone {zone} — Nom"
        )

    @property
    def native_value(self) -> str:
        """Return the Airzone zone name."""
        return self.coordinator.data[
            "zone_data"
        ][self.zone]["name"]


# ============================================================
# ZONE - R26 BITS 0-2
# ============================================================


class AirzoneZoneThermostatOffset(
    CoordinatorEntity[AirzoneCoordinator],
    SensorEntity,
):
    """Thermostat Lite temperature offset."""

    _attr_native_unit_of_measurement = (
        UnitOfTemperature.CELSIUS
    )
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:thermometer-plus"

    def __init__(
        self,
        coordinator,
        entry,
        zone: int,
    ) -> None:
        super().__init__(coordinator)

        self.zone = zone

        self._attr_unique_id = (
            f"{entry.entry_id}_zone_{zone}_thermostat_offset"
        )

        self._attr_name = (
            f"Airzone — Zone {zone} — "
            "Offset température"
        )

    @property
    def native_value(self) -> float:
        """Return thermostat temperature offset."""
        return self.coordinator.data[
            "zone_data"
        ][self.zone]["thermostat_offset"]


# ============================================================
# ZONE - R31
# ============================================================


class AirzoneZoneHumidity(
    CoordinatorEntity[AirzoneCoordinator],
    SensorEntity,
):
    """Zone humidity."""

    _attr_device_class = SensorDeviceClass.HUMIDITY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_icon = "mdi:water-percent"

    def __init__(
        self,
        coordinator,
        entry,
        zone: int,
    ) -> None:
        super().__init__(coordinator)

        self.zone = zone

        self._attr_unique_id = (
            f"{entry.entry_id}_zone_{zone}_humidity"
        )

        self._attr_name = (
            f"Airzone — Zone {zone} — Humidité"
        )

    @property
    def native_value(self) -> int:
        """Return zone humidity."""
        return self.coordinator.data[
            "zone_data"
        ][self.zone]["humidity"]
