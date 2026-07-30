from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, API_URL_ELECTRICITY, API_URL_GAS, RESOURCE_ELECTRICITY, RESOURCE_GAS
from .coordinator import ANWBEnergyCoordinator

PLATFORMS = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    electricity_coordinator = ANWBEnergyCoordinator(hass, API_URL_ELECTRICITY, RESOURCE_ELECTRICITY)
    gas_coordinator = ANWBEnergyCoordinator(hass, API_URL_GAS, RESOURCE_GAS)

    await electricity_coordinator.async_config_entry_first_refresh()
    await gas_coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        RESOURCE_ELECTRICITY: electricity_coordinator,
        RESOURCE_GAS: gas_coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
