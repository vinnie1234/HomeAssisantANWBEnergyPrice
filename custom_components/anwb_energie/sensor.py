from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN,
    RESOURCE_ELECTRICITY,
    RESOURCE_GAS,
    CONF_PRICE_UNIT,
    PRICE_UNIT_EUROS,
)
from .coordinator import ANWBEnergyCoordinator


@dataclass(frozen=True, kw_only=True)
class ANWBSensorDescription(SensorEntityDescription):
    data_key: str
    extra_attrs_fn: Any = None  # callable(data) -> dict | None


def _hourly_attrs(data: dict, use_euros: bool) -> dict:
    hourly = data.get("hourly", {})
    if use_euros:
        hourly = {
            ts: {k: v / 100 if v is not None else None for k, v in prices.items()}
            for ts, prices in hourly.items()
        }
    return {"hourly_prices": hourly}


# Shared sensor templates — used for both electricity and gas
_SENSOR_TEMPLATES: tuple[ANWBSensorDescription, ...] = (
    ANWBSensorDescription(
        key="market_price_current",
        translation_key="market_price_current",
        data_key="current",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        extra_attrs_fn=_hourly_attrs,
    ),
    ANWBSensorDescription(
        key="all_in_price_current",
        translation_key="all_in_price_current",
        data_key="current",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        extra_attrs_fn=_hourly_attrs,
    ),
    ANWBSensorDescription(
        key="market_price_next",
        translation_key="market_price_next",
        data_key="next",
        suggested_display_precision=2,
    ),
    ANWBSensorDescription(
        key="all_in_price_next",
        translation_key="all_in_price_next",
        data_key="next",
        suggested_display_precision=2,
    ),
    ANWBSensorDescription(
        key="market_price_lowest_today",
        translation_key="market_price_lowest_today",
        data_key="market_price_min",
        suggested_display_precision=2,
        icon="mdi:trending-down",
    ),
    ANWBSensorDescription(
        key="market_price_highest_today",
        translation_key="market_price_highest_today",
        data_key="market_price_max",
        suggested_display_precision=2,
        icon="mdi:trending-up",
    ),
    ANWBSensorDescription(
        key="market_price_average_today",
        translation_key="market_price_average_today",
        data_key="market_price_avg",
        suggested_display_precision=2,
        icon="mdi:approximately-equal",
    ),
    ANWBSensorDescription(
        key="all_in_price_lowest_today",
        translation_key="all_in_price_lowest_today",
        data_key="all_in_price_min",
        suggested_display_precision=2,
        icon="mdi:trending-down",
    ),
    ANWBSensorDescription(
        key="all_in_price_highest_today",
        translation_key="all_in_price_highest_today",
        data_key="all_in_price_max",
        suggested_display_precision=2,
        icon="mdi:trending-up",
    ),
    ANWBSensorDescription(
        key="all_in_price_average_today",
        translation_key="all_in_price_average_today",
        data_key="all_in_price_avg",
        suggested_display_precision=2,
        icon="mdi:approximately-equal",
    ),
    ANWBSensorDescription(
        key="all_in_price_cheapest_hour_time",
        translation_key="all_in_price_cheapest_hour_time",
        data_key="all_in_price_cheapest_hour",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:clock-check-outline",
    ),
    ANWBSensorDescription(
        key="all_in_price_most_expensive_hour_time",
        translation_key="all_in_price_most_expensive_hour_time",
        data_key="all_in_price_most_expensive_hour",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:clock-alert-outline",
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
    config = {**entry.data, **entry.options}
    use_euros = config.get(CONF_PRICE_UNIT, "") == PRICE_UNIT_EUROS

    entities = []
    for resource, coordinator in coordinators.items():
        config = _RESOURCE_CONFIG[resource]
        for template in _SENSOR_TEMPLATES:
            if template.key == "market_price_current":
                icon = config["current_icon"]
            elif template.key == "all_in_price_current":
                icon = config["allin_icon"]
            else:
                icon = template.icon

            entities.append(
                ANWBSensor(coordinator, template, resource, config["label"], icon, use_euros)
            )

    async_add_entities(entities)


class ANWBSensor(CoordinatorEntity[ANWBEnergyCoordinator], SensorEntity):
    entity_description: ANWBSensorDescription
    _attr_has_entity_name = True
    _unrecorded_attributes = frozenset({"hourly_prices"})

    def __init__(
        self,
        coordinator: ANWBEnergyCoordinator,
        description: ANWBSensorDescription,
        resource: str,
        label: str,
        icon: str | None,
        use_euros: bool,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._resource = resource
        self._use_euros = use_euros
        self._attr_unique_id = f"anwb_energie_{resource}_{description.key}"
        self._attr_icon = icon
        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, f"{coordinator.config_entry.entry_id}_{resource}")},
            manufacturer="ANWB Energie",
            name=f"ANWB {label} Price",
        )
        if self.entity_description.device_class == SensorDeviceClass.TIMESTAMP:
            self._attr_native_unit_of_measurement = None
        elif self._resource == RESOURCE_GAS:
            self._attr_native_unit_of_measurement = "EUR/m³" if use_euros else "ct/m³"
        else:
            self._attr_native_unit_of_measurement = "EUR/kWh" if use_euros else "ct/kWh"

    def _raw_value(self) -> float | datetime | None:
        data = self.coordinator.data
        if data is None:
            return None

        value = data.get(self.entity_description.data_key)

        if self.entity_description.device_class == SensorDeviceClass.TIMESTAMP:
            if not isinstance(value, dict):
                return None
            timestamp = value.get("time")
            return dt_util.parse_datetime(timestamp) if timestamp else None

        if isinstance(value, dict):
            if "price" in value:
                return value.get("price")
            if "market" in self.entity_description.key:
                return value.get("market_price")
            return value.get("all_in_price")

        return value

    @property
    def native_value(self) -> float | datetime | None:
        raw = self._raw_value()
        if raw is None:
            return None
        if isinstance(raw, datetime):
            return raw
        return raw / 100 if self._use_euros else raw

    @property
    def extra_state_attributes(self) -> dict | None:
        if self.entity_description.extra_attrs_fn is None:
            return None
        data = self.coordinator.data
        if data is None:
            return None
        return self.entity_description.extra_attrs_fn(data, self._use_euros)
