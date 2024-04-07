"""LeakbotEntity class."""

from __future__ import annotations

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import slugify

from .const import ATTRIBUTION, DOMAIN, NAME, VERSION
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
        if key:
            self._attr_unique_id = slugify(f"{DOMAIN}_{id}_{key}")
        else:
            self._attr_unique_id = slugify(f"{DOMAIN}_{id}")

        self.entity_id = f"{platform}.{self._attr_unique_id}"

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, id)},
            name=NAME,
            model=VERSION,
            manufacturer=NAME,
        )

    @property
    def get_device_data(self) -> dict[str, any]:
        """Get the device data."""
        data = self.coordinator.data["devices"][self._device_id]
        return data
