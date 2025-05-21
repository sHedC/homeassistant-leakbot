"""Calendar Sensor for Leakbot."""

from __future__ import annotations

import asyncio

from .entity import LeakbotEntity
from .coordinator import LeakbotDataUpdateCoordinator
from .const import DOMAIN

from datetime import datetime, UTC

from homeassistant.components.calendar import (
    CalendarEntity,
    CalendarEntityDescription,
    CalendarEvent,
)
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
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt

from .const import LOGGER


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
        """Return the next upcoming event."""
        return None

    async def async_added_to_hass(self) -> None:
        """Handle the addition of the calendar to Home Assistant."""
        # Perform initial statistic import when calendar is added.
        await self.update_statistics()
        return await super().async_added_to_hass()

    def _handle_coordinator_update(self) -> None:
        """Handle the update from the coordinator."""
        asyncio.run_coroutine_threadsafe(self.update_statistics(), self.hass.loop)

    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        """Get Calendar Events within a date range."""
        return await self.coordinator.async_get_events(
            self._device_id, start_date, end_date
        )

    async def update_statistics(self) -> None:
        """Update the statistics for the event history."""
        # Update the statistics for the event history.
        # Going to see if we can use the event history to store
        # all calendar events.
        statistic_id = self.entity_id
        statistics_since = datetime.fromtimestamp(0)

        last_stats = await get_instance(self.hass).async_add_executor_job(
            get_last_statistics,
            self.hass,
            1,
            statistic_id,
            False,
            {},
        )

        if last_stats:
            statistics_since = datetime.fromtimestamp(
                last_stats[statistic_id][0].get("end") or 0
            )

        # events = self.get_device_data[self.entity_description.key]
        events = []
        LOGGER.warning(
            "Leakbot Calendar: %s - %s - %s",
            self.entity_id,
            statistics_since,
            last_stats,
        )

        # Update Statistics if needed.
        update_happened = False
        new_stats = []
        for event in reversed(events):
            event_id = event.get("derived_event_id")

            start_date = dt.as_local(
                datetime.strptime(
                    event.get("derived_event_created"), "%Y-%m-%d %H:%M:%S"
                ).replace(tzinfo=UTC)
            )
            closed = event.get("derived_event_closed")
            if closed != "null":
                end_date = dt.as_local(datetime.strptime(closed, "%Y-%m-%d %H:%M:%S"))
            else:
                end_date = start_date

            LOGGER.warning("Start: %s, End: %s", start_date, end_date)

            code = event.get("derived_event_code")
            new_stats.append(StatisticData(start=start_date, state=code))
            update_happened = True

        if update_happened:
            # If we have new statistics, we need to update the calendar
            # with the new statistics.
            new_stats_meta = StatisticMetaData(
                statistic_id=statistic_id,
                source="recorder",
                name=self.name,
                unit_of_measurement=self.unit_of_measurement,
                has_sum=False,
                mean_type=StatisticMeanType.NONE,
            )
            async_import_statistics(self.hass, new_stats_meta, new_stats)
