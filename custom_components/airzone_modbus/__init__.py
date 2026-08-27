"""Intégration Airzone Modbus."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import AirzoneCoordinator


async def async_setup(
    hass: HomeAssistant,
    config: dict,
) -> bool:
    """Configure l'intégration Airzone Modbus."""

    hass.data.setdefault(DOMAIN, {})

    return True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Configure une entrée Airzone Modbus."""

    coordinator = AirzoneCoordinator(
        hass,
        host=entry.data["host"],
        port=entry.data["port"],
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Décharge une entrée Airzone Modbus."""

    hass.data[DOMAIN].pop(entry.entry_id, None)

    return True
