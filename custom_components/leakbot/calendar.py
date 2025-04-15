"""Calendar Sensor for Leakbot."""

from __future__ import annotations

from .entity import LeakbotEntity
from .coordinator import LeakbotDataUpdateCoordinator
from .const import DOMAIN

from datetime import datetime

from homeassistant.components.calendar import (
    CalendarEntity,
    CalendarEntityDescription,
    CalendarEvent,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices: AddEntitiesCallback
):
    """Set up the Calendar Sensors."""
    coordinator: LeakbotDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[LeakbotEntity] = []
    devices: dict[str, any] = coordinator.data.get("devices", {})
    for _, device in devices.items():
        entities.append(
            LeakbotEventsCalendar(
                coordinator,
                device,
                CalendarEntityDescription(
                    key="leakbot_event",
                    translation_key="leakbot_event",
                    has_entity_name=True,
                    name="leakbot_event",
                    icon="mdi:calendar",
                    entity_registry_enabled_default=True,
                    entity_registry_visible_default=True,
                ),
            )
        )

    async_add_devices(entities, True)
    coordinator.remove_old_entities(Platform.CALENDAR)


class LeakbotEventsCalendar(LeakbotEntity, CalendarEntity):
    """Leakbot Events Calendar."""

    def __init__(
        self,
        coordinator: LeakbotDataUpdateCoordinator,
        device: dict[str, any],
        entity_description: CalendarEntityDescription,
    ) -> None:
        """Initialize the calendar."""
        super().__init__(
            Platform.CALENDAR, coordinator, device["id"], entity_description.key
        )
        self.entity_description: CalendarEntityDescription = entity_description

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming event."""
        return None

    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        """Get Calendar Events within a date range."""
        return await self.coordinator.async_get_events(
            self._device_id, start_date, end_date
        )
