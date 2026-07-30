from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
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


SENSORS: tuple[ANWBSensorDescription, ...] = (
    ANWBSensorDescription(
        key="market_price_current",
        name="ANWB Market Price Current",
        data_key="current",
        native_unit_of_measurement="ct/kWh",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=3,
        icon="mdi:lightning-bolt",
        extra_attrs_fn=_hourly_attrs,
    ),
    ANWBSensorDescription(
        key="all_in_price_current",
        name="ANWB All-in Price Current",
        data_key="current",
        native_unit_of_measurement="ct/kWh",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=3,
        icon="mdi:lightning-bolt-circle",
        extra_attrs_fn=_hourly_attrs,
    ),
    ANWBSensorDescription(
        key="market_price_lowest_today",
        name="ANWB Market Price Lowest Today",
        data_key="market_price_min",
        native_unit_of_measurement="ct/kWh",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=3,
        icon="mdi:trending-down",
    ),
    ANWBSensorDescription(
        key="market_price_highest_today",
        name="ANWB Market Price Highest Today",
        data_key="market_price_max",
        native_unit_of_measurement="ct/kWh",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=3,
        icon="mdi:trending-up",
    ),
    ANWBSensorDescription(
        key="market_price_average_today",
        name="ANWB Market Price Average Today",
        data_key="market_price_avg",
        native_unit_of_measurement="ct/kWh",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=3,
        icon="mdi:approximately-equal",
    ),
    ANWBSensorDescription(
        key="all_in_price_lowest_today",
        name="ANWB All-in Price Lowest Today",
        data_key="all_in_price_min",
        native_unit_of_measurement="ct/kWh",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=3,
        icon="mdi:trending-down",
    ),
    ANWBSensorDescription(
        key="all_in_price_highest_today",
        name="ANWB All-in Price Highest Today",
        data_key="all_in_price_max",
        native_unit_of_measurement="ct/kWh",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=3,
        icon="mdi:trending-up",
    ),
    ANWBSensorDescription(
        key="all_in_price_average_today",
        name="ANWB All-in Price Average Today",
        data_key="all_in_price_avg",
        native_unit_of_measurement="ct/kWh",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=3,
        icon="mdi:approximately-equal",
    ),
    ANWBSensorDescription(
        key="market_price_cheapest_hour",
        name="ANWB Market Price Cheapest Hour Today",
        data_key="market_price_cheapest_hour",
        native_unit_of_measurement="ct/kWh",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=3,
        icon="mdi:clock-check-outline",
        extra_attrs_fn=_cheapest_market_attrs,
    ),
    ANWBSensorDescription(
        key="all_in_price_cheapest_hour",
        name="ANWB All-in Price Cheapest Hour Today",
        data_key="all_in_price_cheapest_hour",
        native_unit_of_measurement="ct/kWh",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=3,
        icon="mdi:clock-check-outline",
        extra_attrs_fn=_cheapest_allin_attrs,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: ANWBEnergyCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        ANWBSensor(coordinator, description) for description in SENSORS
    )


class ANWBSensor(CoordinatorEntity[ANWBEnergyCoordinator], SensorEntity):
    entity_description: ANWBSensorDescription

    def __init__(
        self,
        coordinator: ANWBEnergyCoordinator,
        description: ANWBSensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"anwb_energy_{description.key}"

    @property
    def native_value(self) -> float | None:
        data = self.coordinator.data
        if data is None:
            return None

        value = data.get(self.entity_description.data_key)

        if isinstance(value, dict):
            # cheapest_hour entries have a "price" key
            if "price" in value:
                return value.get("price")
            # current entry has market_price / all_in_price
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
