"""Binary sensors for Airzone Modbus."""

from **future** import annotations

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


coordinator: AirzoneCoordinator = hass.data[
    DOMAIN
][entry.entry_id]

entities = []

for zone in coordinator.data["zones"]:
    entities.extend(
        [
            AirzoneZoneLocalVentilation(
                coordinator,
                entry,
                zone,
            ),
            AirzoneZoneBit15(
                coordinator,
                entry,
                zone,
            ),
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


# ============================================================

# ZONE - R00 BIT 0

# Ventilation locale

# ============================================================

class AirzoneZoneLocalVentilation(
CoordinatorEntity[AirzoneCoordinator],
BinarySensorEntity,
):
"""R00 bit 0 - Ventilation locale."""


_attr_device_class = BinarySensorDeviceClass.RUNNING

def __init__(
    self,
    coordinator,
    entry: ConfigEntry,
    zone: int,
) -> None:
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
    """Return whether local ventilation is active."""
    return self.coordinator.data["zone_data"][
        self.zone
    ]["local_ventilation"]


# ============================================================

# ZONE - R00 BIT 15

# Fonction dépendante du système

# ============================================================

class AirzoneZoneBit15(
CoordinatorEntity[AirzoneCoordinator],
BinarySensorEntity,
):
"""R00 bit 15 - Fonction dépendante du système."""


def __init__(
    self,
    coordinator,
    entry: ConfigEntry,
    zone: int,
) -> None:
    super().__init__(coordinator)

    self.zone = zone

    self._attr_unique_id = (
        f"{entry.entry_id}_zone_{zone}_bit15"
    )

    self._attr_name = (
        f"Airzone — Zone {zone} — Bit 15"
    )

@property
def is_on(self) -> bool:
    """Return the value of bit 15."""
    return self.coordinator.data["zone_data"][
        self.zone
    ]["bit15"]
```

# ============================================================

# ZONE - R26 BIT 3

# LED thermostat Lite

# ============================================================

class AirzoneZoneThermostatLed(
CoordinatorEntity[AirzoneCoordinator],
BinarySensorEntity,
):
"""R26 bit 3 - LED thermostat Lite."""


_attr_device_class = BinarySensorDeviceClass.RUNNING

def __init__(
    self,
    coordinator,
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
```

# ============================================================

# ZONE - R26 BIT 5

# Thermostat Lite présent

# ============================================================

class AirzoneZoneThermostatLitePresent(
CoordinatorEntity[AirzoneCoordinator],
BinarySensorEntity,
):
"""R26 bit 5 - Thermostat Lite présent."""


_attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

def __init__(
    self,
    coordinator,
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
