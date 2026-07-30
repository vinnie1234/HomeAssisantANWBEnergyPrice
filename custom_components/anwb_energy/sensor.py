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
from homeassistant.const import UnitOfEnergy
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import ANWBEnergyCoordinator

EURO_PER_KWH = "€/kWh"  # HA has no built-in unit for this price type


@dataclass(frozen=True, kw_only=True)
class ANWBSensorDescription(SensorEntityDescription):
    data_key: str
    extra_attrs_fn: Any = None  # callable(data) -> dict | None


def _hourly_attrs(data: dict) -> dict:
    return {"tarieven_per_uur": data.get("hourly", {})}


def _goedkoopste_markt_attrs(data: dict) -> dict | None:
    entry = data.get("marktprijs_goedkoopste_uur")
    if entry is None:
        return None
    return {"tijdstip": entry["tijdstip"]}


def _goedkoopste_allin_attrs(data: dict) -> dict | None:
    entry = data.get("allinprijs_goedkoopste_uur")
    if entry is None:
        return None
    return {"tijdstip": entry["tijdstip"]}


SENSORS: tuple[ANWBSensorDescription, ...] = (
    ANWBSensorDescription(
        key="marktprijs_huidig",
        name="ANWB Marktprijs Huidig",
        data_key="current",
        native_unit_of_measurement="ct/kWh",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=3,
        icon="mdi:lightning-bolt",
        extra_attrs_fn=_hourly_attrs,
    ),
    ANWBSensorDescription(
        key="allinprijs_huidig",
        name="ANWB All-in Prijs Huidig",
        data_key="current",
        native_unit_of_measurement="ct/kWh",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=3,
        icon="mdi:lightning-bolt-circle",
        extra_attrs_fn=_hourly_attrs,
    ),
    ANWBSensorDescription(
        key="marktprijs_min",
        name="ANWB Marktprijs Laagste Vandaag",
        data_key="marktprijs_min",
        native_unit_of_measurement="ct/kWh",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=3,
        icon="mdi:trending-down",
    ),
    ANWBSensorDescription(
        key="marktprijs_max",
        name="ANWB Marktprijs Hoogste Vandaag",
        data_key="marktprijs_max",
        native_unit_of_measurement="ct/kWh",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=3,
        icon="mdi:trending-up",
    ),
    ANWBSensorDescription(
        key="marktprijs_avg",
        name="ANWB Marktprijs Gemiddeld Vandaag",
        data_key="marktprijs_avg",
        native_unit_of_measurement="ct/kWh",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=3,
        icon="mdi:approximately-equal",
    ),
    ANWBSensorDescription(
        key="allinprijs_min",
        name="ANWB All-in Prijs Laagste Vandaag",
        data_key="allinprijs_min",
        native_unit_of_measurement="ct/kWh",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=3,
        icon="mdi:trending-down",
    ),
    ANWBSensorDescription(
        key="allinprijs_max",
        name="ANWB All-in Prijs Hoogste Vandaag",
        data_key="allinprijs_max",
        native_unit_of_measurement="ct/kWh",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=3,
        icon="mdi:trending-up",
    ),
    ANWBSensorDescription(
        key="allinprijs_avg",
        name="ANWB All-in Prijs Gemiddeld Vandaag",
        data_key="allinprijs_avg",
        native_unit_of_measurement="ct/kWh",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=3,
        icon="mdi:approximately-equal",
    ),
    ANWBSensorDescription(
        key="marktprijs_goedkoopste_uur",
        name="ANWB Marktprijs Goedkoopste Uur Vandaag",
        data_key="marktprijs_goedkoopste_uur",
        native_unit_of_measurement="ct/kWh",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=3,
        icon="mdi:clock-check-outline",
        extra_attrs_fn=_goedkoopste_markt_attrs,
    ),
    ANWBSensorDescription(
        key="allinprijs_goedkoopste_uur",
        name="ANWB All-in Prijs Goedkoopste Uur Vandaag",
        data_key="allinprijs_goedkoopste_uur",
        native_unit_of_measurement="ct/kWh",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=3,
        icon="mdi:clock-check-outline",
        extra_attrs_fn=_goedkoopste_allin_attrs,
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

        key = self.entity_description.data_key
        value = data.get(key)

        if isinstance(value, dict):
            # goedkoopste_uur entries have a "prijs" key
            if "prijs" in value:
                return value.get("prijs")
            # current entry has marktprijs / allinPrijs
            if "marktprijs" in self.entity_description.key:
                return value.get("marktprijs")
            return value.get("allinPrijs")

        return value

    @property
    def extra_state_attributes(self) -> dict | None:
        if self.entity_description.extra_attrs_fn is None:
            return None
        data = self.coordinator.data
        if data is None:
            return None
        return self.entity_description.extra_attrs_fn(data)
