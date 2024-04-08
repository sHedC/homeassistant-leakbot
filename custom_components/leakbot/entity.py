"""LeakbotEntity class."""

from __future__ import annotations

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import slugify

from .const import ATTRIBUTION, DOMAIN, NAME
from .coordinator import LeakbotDataUpdateCoordinator


class LeakbotEntity(CoordinatorEntity):
    """LeakbotEntity class."""

    _attr_attribution = ATTRIBUTION

    def __init__(
        self,
        platform: str,
        coordinator: LeakbotDataUpdateCoordinator,
        id: str,
        key: str | None = None,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._device_id = id
        self._leakbot_id = self.get_device_data["leakbotId"]

        if key:
            self._attr_unique_id = slugify(f"{DOMAIN}_{self._leakbot_id}_{key}")
        else:
            self._attr_unique_id = slugify(f"{DOMAIN}_{self._leakbot_id}")
        self.entity_id = f"{platform}.{self._attr_unique_id}"

        # If the entity is found in existing entities, remove it.
        if platform in coordinator.old_entries:
            if self.entity_id in coordinator.old_entries[platform]:
                entity_ids: list[str] = coordinator.old_entries[platform]
                entity_index = entity_ids.index(self.entity_id)
                entity_ids.pop(entity_index)

    @property
    def get_device_data(self) -> dict[str, any]:
        """Get the device data."""
        data = self.coordinator.data["devices"][self._device_id]
        return data

    @property
    def device_info(self):
        """Return the device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=f"{NAME} {self._leakbot_id}",
            manufacturer=NAME,
            model=self.get_device_data["device_type"],
            sw_version=self.get_device_data["fw_version"],
            hw_version=self._leakbot_id,
            via_device=(DOMAIN, self.get_device_data["leakbotId"]),
        )
