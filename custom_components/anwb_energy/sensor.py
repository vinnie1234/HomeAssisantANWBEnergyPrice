from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, RESOURCE_ELECTRICITY, RESOURCE_GAS
from .coordinator import ANWBEnergyCoordinator


@dataclass(frozen=True, kw_only=True)
class ANWBSensorDescription(SensorEntityDescription):
    data_key: str
    extra_attrs_fn: Any = None  # callable(data) -> dict | None


def _hourly_attrs(data: dict) -> dict:
    return {"hourly_prices": data.get("hourly", {})}


def _cheapest_market_attrs(data: dict) -> dict | None:
    entry = data.get("market_price_cheapest_hour")
    if entry is None:
        return None
    return {"time": entry["time"]}


def _cheapest_allin_attrs(data: dict) -> dict | None:
    entry = data.get("all_in_price_cheapest_hour")
    if entry is None:
        return None
    return {"time": entry["time"]}


# Shared sensor template — used for both electricity and gas
_SENSOR_TEMPLATES: tuple[ANWBSensorDescription, ...] = (
    ANWBSensorDescription(
        key="market_price_current",
        name="Market Price Current",
        data_key="current",
        native_unit_of_measurement="ct/kWh",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=3,
        extra_attrs_fn=_hourly_attrs,
    ),
    ANWBSensorDescription(
        key="all_in_price_current",
        name="All-in Price Current",
        data_key="current",
        native_unit_of_measurement="ct/kWh",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=3,
        extra_attrs_fn=_hourly_attrs,
    ),
    ANWBSensorDescription(
        key="market_price_lowest_today",
        name="Market Price Lowest Today",
        data_key="market_price_min",
        native_unit_of_measurement="ct/kWh",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=3,
        icon="mdi:trending-down",
    ),
    ANWBSensorDescription(
        key="market_price_highest_today",
        name="Market Price Highest Today",
        data_key="market_price_max",
        native_unit_of_measurement="ct/kWh",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=3,
        icon="mdi:trending-up",
    ),
    ANWBSensorDescription(
        key="market_price_average_today",
        name="Market Price Average Today",
        data_key="market_price_avg",
        native_unit_of_measurement="ct/kWh",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=3,
        icon="mdi:approximately-equal",
    ),
    ANWBSensorDescription(
        key="all_in_price_lowest_today",
        name="All-in Price Lowest Today",
        data_key="all_in_price_min",
        native_unit_of_measurement="ct/kWh",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=3,
        icon="mdi:trending-down",
    ),
    ANWBSensorDescription(
        key="all_in_price_highest_today",
        name="All-in Price Highest Today",
        data_key="all_in_price_max",
        native_unit_of_measurement="ct/kWh",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=3,
        icon="mdi:trending-up",
    ),
    ANWBSensorDescription(
        key="all_in_price_average_today",
        name="All-in Price Average Today",
        data_key="all_in_price_avg",
        native_unit_of_measurement="ct/kWh",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=3,
        icon="mdi:approximately-equal",
    ),
    ANWBSensorDescription(
        key="market_price_cheapest_hour",
        name="Market Price Cheapest Hour Today",
        data_key="market_price_cheapest_hour",
        native_unit_of_measurement="ct/kWh",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=3,
        icon="mdi:clock-check-outline",
        extra_attrs_fn=_cheapest_market_attrs,
    ),
    ANWBSensorDescription(
        key="all_in_price_cheapest_hour",
        name="All-in Price Cheapest Hour Today",
        data_key="all_in_price_cheapest_hour",
        native_unit_of_measurement="ct/kWh",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=3,
        icon="mdi:clock-check-outline",
        extra_attrs_fn=_cheapest_allin_attrs,
    ),
)

_RESOURCE_CONFIG = {
    RESOURCE_ELECTRICITY: {
        "label": "Electricity",
        "current_icon": "mdi:lightning-bolt",
        "allin_icon": "mdi:lightning-bolt-circle",
    },
    RESOURCE_GAS: {
        "label": "Gas",
        "current_icon": "mdi:fire",
        "allin_icon": "mdi:fire-circle",
    },
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinators: dict[str, ANWBEnergyCoordinator] = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for resource, coordinator in coordinators.items():
        config = _RESOURCE_CONFIG[resource]
        for template in _SENSOR_TEMPLATES:
            # Pick correct icon for current-price sensors
            if template.key == "market_price_current":
                icon = config["current_icon"]
            elif template.key == "all_in_price_current":
                icon = config["allin_icon"]
            else:
                icon = template.icon

            entities.append(ANWBSensor(coordinator, template, resource, config["label"], icon))

    async_add_entities(entities)


class ANWBSensor(CoordinatorEntity[ANWBEnergyCoordinator], SensorEntity):
    entity_description: ANWBSensorDescription

    def __init__(
        self,
        coordinator: ANWBEnergyCoordinator,
        description: ANWBSensorDescription,
        resource: str,
        label: str,
        icon: str | None,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._resource = resource
        self._attr_unique_id = f"anwb_energy_{resource}_{description.key}"
        self._attr_name = f"ANWB {label} {description.name}"
        self._attr_icon = icon

    @property
    def native_value(self) -> float | None:
        data = self.coordinator.data
        if data is None:
            return None

        value = data.get(self.entity_description.data_key)

        if isinstance(value, dict):
            if "price" in value:
                return value.get("price")
            if "market" in self.entity_description.key:
                return value.get("market_price")
            return value.get("all_in_price")

        return value

    @property
    def extra_state_attributes(self) -> dict | None:
        if self.entity_description.extra_attrs_fn is None:
            return None
        data = self.coordinator.data
        if data is None:
            return None
        return self.entity_description.extra_attrs_fn(data)
