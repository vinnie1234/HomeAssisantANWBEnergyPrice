from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import (
    DOMAIN,
    API_URL_ELECTRICITY,
    API_URL_GAS,
    RESOURCE_ELECTRICITY,
    RESOURCE_GAS,
    CONF_ELECTRICITY,
    CONF_GAS,
)
from .coordinator import ANWBEnergyCoordinator

PLATFORMS = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    coordinators = {}

    if entry.data.get(CONF_ELECTRICITY, True):
        coordinator = ANWBEnergyCoordinator(hass, API_URL_ELECTRICITY, RESOURCE_ELECTRICITY)
        await coordinator.async_config_entry_first_refresh()
        coordinators[RESOURCE_ELECTRICITY] = coordinator

    if entry.data.get(CONF_GAS, True):
        coordinator = ANWBEnergyCoordinator(hass, API_URL_GAS, RESOURCE_GAS)
        await coordinator.async_config_entry_first_refresh()
        coordinators[RESOURCE_GAS] = coordinator

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinators

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
