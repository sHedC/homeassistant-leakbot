"""Leakbot Device Tracker."""

from homeassistant.components.device_tracker import ScannerEntity, SourceType
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import LeakbotDataUpdateCoordinator
from .entity import LeakbotEntity

# TODO: Find out abut callback restore_entities and add_new_entities (ruckus_unleashed)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Load Entities from the config settings."""
    coordinator: LeakbotDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[LeakbotEntity] = []
    devices: dict[str, any] = coordinator.data.get("devices", {})
    for _, device in devices.items():
        entities.append(LeadbotDevice(coordinator, device))

    async_add_entities(entities, True)
    coordinator.remove_old_entities(Platform.DEVICE_TRACKER)  # Probably not needed.


class LeadbotDevice(LeakbotEntity, ScannerEntity):
    """Leakbot Device."""

    def __init__(
        self,
        coordinator: LeakbotDataUpdateCoordinator,
        device: dict[str, any],
    ):
        """Initialise Leakbot Device Entity."""
        super().__init__(Platform.DEVICE_TRACKER, coordinator, device["id"])
        self._attr_icon = "mdi:water-check-outline"

    @property
    def source_type(self) -> SourceType | str:
        """Return the source type, eg gps or router, of the device."""
        return "detector"

    @property
    def is_connected(self) -> bool:
        """Return if connected."""
        return True

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.get_device_data["device_status"]

    @property
    def extra_state_attributes(self):
        """Attributes."""
        device = self.get_device_data

        result = {}
        result["device_type"] = device["device_type"]

        return result
