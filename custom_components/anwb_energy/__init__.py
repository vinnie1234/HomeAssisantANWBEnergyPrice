from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_change

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
        coordinators[RESOURCE_ELECTRICITY] = ANWBEnergyCoordinator(
            hass, API_URL_ELECTRICITY, RESOURCE_ELECTRICITY
        )

    if entry.data.get(CONF_GAS, True):
        coordinators[RESOURCE_GAS] = ANWBEnergyCoordinator(hass, API_URL_GAS, RESOURCE_GAS)

    # A failed first fetch must not block setup: the sensors stay registered
    # (unavailable) and the hourly refresh below retries.
    for coordinator in coordinators.values():
        await coordinator.async_refresh()

    async def _hourly_refresh(_now) -> None:
        for coordinator in coordinators.values():
            await coordinator.async_refresh()

    entry.async_on_unload(
        async_track_time_change(hass, _hourly_refresh, minute=0, second=5)
    )

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinators

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
