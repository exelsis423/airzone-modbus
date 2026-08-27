"""Intégration Airzone Modbus."""

from homeassistant.core import HomeAssistant

from .const import DOMAIN


async def async_setup(
    hass: HomeAssistant,
    config: dict,
) -> bool:
    """Configure l'intégration Airzone Modbus."""

    hass.data.setdefault(DOMAIN, {})

    return True
