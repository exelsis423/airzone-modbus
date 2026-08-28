"""Binary sensors for Airzone Modbus."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
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
                AirzoneZoneThermostatLed(
                    coordinator,
                    entry,
                    zone,
                ),
                AirzoneZoneThermostatLitePresent(
                    coordinator,
                    entry,
                    zone,
                ),
            ]
        )

    async_add_entities(entities)


class AirzoneZoneThermostatLed(
    CoordinatorEntity[AirzoneCoordinator],
    BinarySensorEntity,
):
    """Thermostat Lite status LED."""

    _attr_device_class = BinarySensorDeviceClass.RUNNING

    def __init__(
        self,
        coordinator: AirzoneCoordinator,
        entry: ConfigEntry,
        zone: int,
    ) -> None:
        super().__init__(coordinator)

        self.zone = zone

        self._attr_unique_id = (
            f"{entry.entry_id}_zone_{zone}_thermostat_led"
        )
        self._attr_name = (
            f"Airzone — Zone {zone} — LED thermostat"
        )

    @property
    def is_on(self) -> bool:
        """Return whether the thermostat LED is on."""

        return self.coordinator.data["zone_data"][
            self.zone
        ]["thermostat_led"]


class AirzoneZoneThermostatLitePresent(
    CoordinatorEntity[AirzoneCoordinator],
    BinarySensorEntity,
):
    """Thermostat Lite presence."""

    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    def __init__(
        self,
        coordinator: AirzoneCoordinator,
        entry: ConfigEntry,
        zone: int,
    ) -> None:
        super().__init__(coordinator)

        self.zone = zone

        self._attr_unique_id = (
            f"{entry.entry_id}_zone_{zone}_thermostat_lite"
        )
        self._attr_name = (
            f"Airzone — Zone {zone} — Thermostat Lite"
        )

    @property
    def is_on(self) -> bool:
        """Return whether a thermostat Lite is present."""

        return self.coordinator.data["zone_data"][
            self.zone
        ]["thermostat_lite_present"]
