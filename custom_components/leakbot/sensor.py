"""Sensor platform for Leakbot."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import LeakbotDataUpdateCoordinator
from .entity import LeakbotEntity


@dataclass
class LeakbotSensorEntityDescription(SensorEntityDescription):
    """Leakbot Sensor Entity Description."""

    lookup_keys: str = None


ENTITY_DESCRIPTIONS = (
    LeakbotSensorEntityDescription(
        key="device_status",
        name="Device Status",
        icon="mdi:water-check-outline",
    ),
    LeakbotSensorEntityDescription(
        lookup_keys="info",
        key="battery_sm",
        name="Battery Status",
        icon="mdi:battery80",
    ),
    LeakbotSensorEntityDescription(
        lookup_keys="info.leak_count_summary",
        key="leak_free_days",
        name="Leak Free Days",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.DAYS,
        suggested_unit_of_measurement=UnitOfTime.DAYS,
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
    def native_value(self) -> str:
        """Return the native value of the sensor."""
        sub_data = self.get_device_data

        # Get the Data Subset.
        if self.entity_description.lookup_keys:
            for sub_key in self.entity_description.lookup_keys.split("."):
                sub_data = sub_data[sub_key]

        return sub_data[self._key]
