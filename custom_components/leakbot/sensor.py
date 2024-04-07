"""Sensor platform for Leakbot."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import LeakbotDataUpdateCoordinator
from .entity import LeakbotEntity

ENTITY_DESCRIPTIONS = (
    SensorEntityDescription(
        key="device_status",
        name="Device Status",
        icon="mdi:water-check-outline",
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
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(
            Platform.SENSOR, coordinator, device["id"], entity_description.key
        )
        self.entity_description = entity_description

    @property
    def native_value(self) -> str:
        """Return the native value of the sensor."""
        # Here we get from data->devices->device_id->device_status
        return self.get_device_data["device_status"]
