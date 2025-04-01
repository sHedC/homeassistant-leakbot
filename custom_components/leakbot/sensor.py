"""Sensor platform for Leakbot."""

from __future__ import annotations
from .entity import LeakbotEntity
from .coordinator import LeakbotDataUpdateCoordinator
from .const import DOMAIN
from homeassistant_historical_sensor import HistoricalSensor, HistoricalState, PollUpdateMixin

from decimal import Decimal
from dataclasses import dataclass
from datetime import date, datetime, timedelta

from homeassistant.components.recorder.models import StatisticData, StatisticMetaData
from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform, UnitOfTime, UnitOfVolume
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.util import slugify, dt

from .const import LOGGER


@dataclass
class LeakbotSensorEntityDescription(SensorEntityDescription):
    """Leakbot Sensor Entity Description."""

    data_type: str = "str"
    lookup_keys: str = None


ENTITY_DESCRIPTIONS = (
    LeakbotSensorEntityDescription(
        key="device_status",
        translation_key="device_status",
        has_entity_name=True,
        icon="mdi:water-check-outline",
    ),
    LeakbotSensorEntityDescription(
        lookup_keys="info",
        key="battery_sm",
        translation_key="battery_sm",
        has_entity_name=True,
        icon="mdi:battery",
    ),
    LeakbotSensorEntityDescription(
        lookup_keys="info.leak_count_summary",
        key="leak_free_days",
        translation_key="leak_free_days",
        has_entity_name=True,
        data_type="int",
        suggested_display_precision=0,
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.DAYS,
        suggested_unit_of_measurement=UnitOfTime.DAYS,
        unit_of_measurement=UnitOfTime.DAYS,
    ),
    LeakbotSensorEntityDescription(
        lookup_keys="last_update",
        key="messageTimestamp",
        translation_key="last_update",
        has_entity_name=True,
        data_type="timestamp",
        device_class=SensorDeviceClass.TIMESTAMP,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices: AddEntitiesCallback
):
    """Set up the sensor platform."""
    coordinator: LeakbotDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[LeakbotEntity] = []
    devices: dict[str, any] = coordinator.data.get("devices", {})
    for _, device in devices.items():
        for entity_description in ENTITY_DESCRIPTIONS:
            entities.append(LeakbotSensor(coordinator, device, entity_description))

        entities.append(
            LeakbotHistoricalSensor(
                coordinator, device, LeakbotSensorEntityDescription(
                    key="water_usage",
                    translation_key="water_usage",
                    has_entity_name=True,
                    name="water_usage",
                    entity_registry_enabled_default=True,
                    state_class=None,
                    device_class=SensorDeviceClass.WATER,
                    native_unit_of_measurement=UnitOfVolume.LITERS,
                )
            )
        )

    async_add_devices(entities, True)
    coordinator.remove_old_entities(Platform.SENSOR)


class LeakbotSensor(LeakbotEntity, SensorEntity):
    """Leakbot Sensor class."""

    def __init__(
        self,
        coordinator: LeakbotDataUpdateCoordinator,
        device: dict[str, any],
        entity_description: LeakbotSensorEntityDescription,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(
            Platform.SENSOR, coordinator, device["id"], entity_description.key
        )
        self.entity_description: LeakbotSensorEntityDescription = entity_description

    @property
    def native_value(self) -> StateType | date | datetime | Decimal:
        """Return the native value of the sensor."""
        sub_data = self.get_device_data

        # Get the Data Subset.
        if self.entity_description.lookup_keys:
            for sub_key in self.entity_description.lookup_keys.split("."):
                sub_data = sub_data[sub_key]

        return_value = sub_data[self.entity_description.key]
        match self.entity_description.data_type:
            case "int":
                return int(return_value)
            case "timestamp":
                # Format: "2022-03-19 13:10:18"
                return datetime.fromisoformat(f"{return_value}+00:00")
            case _:
                return slugify(return_value)


class LeakbotHistoricalSensor(LeakbotEntity, PollUpdateMixin, HistoricalSensor, SensorEntity):
    """Leakbot Historical Sensor class."""

    def __init__(
        self,
        coordinator: LeakbotDataUpdateCoordinator,
        device: dict[str, any],
        entity_description: LeakbotSensorEntityDescription,
    ) -> None:
        """Initialize the historical sensor class."""
        super().__init__(
            Platform.SENSOR, coordinator, device["id"], entity_description.key
        )
        self.entity_description: LeakbotSensorEntityDescription = entity_description
        self._attr_state = None

    async def async_added_to_hass(self) -> None:
        """Handle the addition of the sensor to Home Assistant."""
        await super().async_added_to_hass()

    async def async_update_historical(self):
        """Update the historical data for the sensor."""
        water_usage = self.get_device_data["water_usage"]

        # Get the current query time and step through history.
        query_date = dt.as_local(datetime.fromtimestamp(water_usage["ts"] / 1000))
        query_date = query_date.replace(hour=0, minute=0, second=0, microsecond=0)
        LOGGER.debug("Query Date: %s", query_date)
        water_states = []
        for day in water_usage["days"]:
            water_states.append(
                HistoricalState(
                    state=int(day["details"]["total"]),
                    dt=query_date + timedelta(days=int(day["offset"]))
                )
            )
        self._attr_historical_states = water_states

    @property
    def statistic_id(self) -> str:
        """Return the statistic ID for the sensor."""
        return self.entity_id

    def get_statistic_metadata(self) -> StatisticMetaData:
        """Return the statistic metadata for the sensor."""
        meta = super().get_statistic_metadata()
        meta["has_sum"] = True
        meta["has_mean"] = False

        return meta

    async def async_calculate_statistic_data(
        self, hist_states: list[HistoricalState], *, latest: dict | None = None
    ) -> list[StatisticData]:
        """Group and calculate statistical data."""
        accumulated = latest["sum"] if latest else 0

        ret = []
        for hist_state in hist_states:
            accumulated += hist_state.state
            ret.append(
                StatisticData(
                    start=hist_state.dt,
                    end=hist_state.dt + timedelta(days=1),
                    sum=accumulated,
                    count=1,
                    mean=None,
                )
            )

        return ret
