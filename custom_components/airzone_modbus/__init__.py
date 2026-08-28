"""Intégration Airzone Modbus."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN


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

    from .coordinator import AirzoneCoordinator

    coordinator = AirzoneCoordinator(
        hass,
        host=entry.data["host"],
        port=entry.data["port"],
        slave=entry.data["slave"],
        update_interval=entry.data["update_interval"],
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(
        entry,
        [
            "sensor",
            "binary_sensor",
            "select",
            "switch",
        ],
    )

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Décharge une entrée Airzone Modbus."""

    unload_ok = await hass.config_entries.async_unload_platforms(
        entry,
        [
            "sensor",
            "binary_sensor",
            "select",
            "switch",
        ],
    )

    if unload_ok:
        hass.data[DOMAIN].pop(
            entry.entry_id,
            None,
        )

    return unload_ok
