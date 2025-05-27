"""Calendar Sensor for Leakbot."""

from __future__ import annotations

from .entity import LeakbotEntity
from .coordinator import LeakbotDataUpdateCoordinator
from .const import DOMAIN

from datetime import date, datetime, timedelta

from ical.calendar import Calendar
from ical.event import Event

from homeassistant.components.calendar import (
    CalendarEntity,
    CalendarEntityDescription,
    CalendarEvent,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt


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
                    key="events",
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
        """The currently active or next event."""
        # Always None as active events with no end date don't work well.
        # The active status is in the State sensor.
        return None

    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        """Get Calendar Events within a date range."""
        dev_calendar: Calendar = self.get_device_data.get("calendar")
        events = dev_calendar.timeline_tz(start_date.tzinfo).overlapping(
            start_date,
            end_date,
        )
        return [_get_calendar_event(event) for event in events]


def _get_calendar_event(event: Event) -> CalendarEvent:
    """Return a CalendarEvent."""
    start: datetime | date
    end: datetime | date
    if isinstance(event.start, datetime) and isinstance(event.end, datetime):
        start = dt.as_local(event.start)
        end = dt.as_local(event.end)
        if (end - start) <= timedelta(seconds=0):
            end = start + timedelta(minutes=30)
    else:
        start = event.start
        end = event.end
        if (end - start) < timedelta(days=0):
            end = start + timedelta(days=1)

    return CalendarEvent(
        summary=event.summary,
        start=start,
        end=end,
        description=event.description,
        uid=event.uid,
        rrule=event.rrule.as_rrule_str() if event.rrule else None,
        recurrence_id=event.recurrence_id,
        location=event.location,
    )
