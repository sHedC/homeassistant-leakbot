"""Sensor platform for Leakbot."""

from __future__ import annotations

import asyncio

from .entity import LeakbotEntity
from .coordinator import LeakbotDataUpdateCoordinator
from .const import DOMAIN

from decimal import Decimal
from dataclasses import dataclass
from datetime import date, datetime, timedelta

from homeassistant.components.recorder.models import (
    StatisticData,
    StatisticMetaData,
    StatisticMeanType,
)
from homeassistant.components.recorder.statistics import (
    async_import_statistics,
    get_instance,
    get_last_statistics,
)
from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform, UnitOfTime
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

        try:
            get_instance(hass)
        except KeyError:  # No recorder loaded
            LOGGER.warning("Recorder not loaded, disabling history sensor.")
        else:
            entities.append(
                LeakbotWaterHistorySensor(
                    coordinator,
                    device,
                    LeakbotSensorEntityDescription(
                        key="water_usage",
                        translation_key="water_usage_events",
                        has_entity_name=True,
                        name="water_usage_events",
                        entity_registry_enabled_default=True,
                        state_class=None,
                        device_class=SensorDeviceClass.WATER,
                        native_unit_of_measurement=None,
                    ),
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


class LeakbotWaterHistorySensor(LeakbotEntity, SensorEntity):
    """Leakbot Water Usage Sensor class, used for historical data."""

    def __init__(
        self,
        coordinator: LeakbotDataUpdateCoordinator,
        device: dict[str, any],
        entity_description: LeakbotSensorEntityDescription,
    ) -> None:
        """Initialize the water usage sensor class."""
        super().__init__(
            Platform.SENSOR, coordinator, device["id"], entity_description.key
        )
        self.entity_description: LeakbotSensorEntityDescription = entity_description
        self._attr_state = None

    @property
    def state(self) -> StateType | date | datetime | Decimal:
        """Return the native value of the sensor."""
        # Returns none as there is no current state for this sensor.
        # This is a historical sensor.
        return None

    async def async_added_to_hass(self) -> None:
        """Handle the addition of the sensor to Home Assistant."""
        # Perform initial statistic import when sensor is added.
        await self.update_statistics()
        return await super().async_added_to_hass()

    def _handle_coordinator_update(self) -> None:
        """Handle the update from the coordinator."""
        asyncio.run_coroutine_threadsafe(self.update_statistics(), self.hass.loop)

    async def update_statistics(self) -> None:
        """Update the statistics for the water usage sensor."""
        # Update the statistics for the water usage sensor.
        # This is a historical sensor and does not have a current state.
        statistic_id = self.entity_id
        statistics_sum = 0
        statistics_since = datetime.fromtimestamp(0)

        last_stats = await get_instance(self.hass).async_add_executor_job(
            get_last_statistics,
            self.hass,
            1,
            statistic_id,
            False,
            {"sum"},
        )

        if last_stats:
            statistics_sum = last_stats[statistic_id][0].get("sum") or 0
            statistics_since = datetime.fromtimestamp(
                last_stats[statistic_id][0].get("end") or 0
            )

        # Last Start: 2025-04-05 18:00:00 :: End 2025-04-05 18:00:00
        water_usage = self.get_device_data[self.entity_description.key]
        query_date = dt.as_local(datetime.fromtimestamp(water_usage["ts"] / 1000))
        query_date = query_date.replace(hour=0, minute=0, second=0, microsecond=0)

        update_happened = False
        new_stats = []
        for day in reversed(water_usage["days"]):
            start_date = query_date + timedelta(days=int(day["offset"]))
            if start_date > dt.as_local(statistics_since):
                update_happened = True

                statistics_sum += float(day["details"]["night"]) / 2
                new_stats.append(
                    StatisticData(
                        start=query_date.replace(hour=0)
                        + timedelta(days=int(day["offset"])),
                        state=float(day["details"]["night"]) / 2,
                        sum=statistics_sum,
                    )
                )
                statistics_sum += float(day["details"]["morning"]) / 2
                new_stats.append(
                    StatisticData(
                        start=query_date.replace(hour=6)
                        + timedelta(days=int(day["offset"])),
                        state=float(day["details"]["morning"]) / 2,
                        sum=statistics_sum,
                    )
                )
                statistics_sum += float(day["details"]["afternoon"]) / 2
                new_stats.append(
                    StatisticData(
                        start=query_date.replace(hour=12)
                        + timedelta(days=int(day["offset"])),
                        state=float(day["details"]["afternoon"]) / 2,
                        sum=statistics_sum,
                    )
                )
                statistics_sum += float(day["details"]["evening"]) / 2
                new_stats.append(
                    StatisticData(
                        start=query_date.replace(hour=18)
                        + timedelta(days=int(day["offset"])),
                        state=float(day["details"]["evening"]) / 2,
                        sum=statistics_sum,
                    )
                )

        if update_happened:
            # Import the statistics into the database.
            new_stats_meta = StatisticMetaData(
                mean_type=StatisticMeanType.NONE,
                has_sum=True,
                name=self.name,
                source="recorder",
                statistic_id=statistic_id,
                unit_of_measurement=self.unit_of_measurement,
            )
            async_import_statistics(self.hass, new_stats_meta, new_stats)
