import logging
import datetime
import uuid
from homeassistant.components.calendar import CalendarEntity
from homeassistant.components.calendar import CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.util.dt import parse_datetime, utcnow
from homeassistant.util import dt as dt_util
from datetime import timedelta
from datetime import timezone
from .const import DOMAIN


_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up hygiene calendar."""
    _LOGGER.info("📅 Setting up HygieneCalendar for TestChair")

    if DOMAIN not in hass.data or entry.entry_id not in hass.data[DOMAIN]:
        _LOGGER.error("❌ Integration data missing for calendar setup")
        return
    integration_data = hass.data[DOMAIN][entry.entry_id]
    device_name = integration_data.get("device_name", "Test Chair")

    calendar_entity = HygieneCalendar(
        name=f"Hygiene Plan: {device_name}",
        unique_id=f"{entry.entry_id}_hygiene_plan"
    )

    hass.data[DOMAIN][entry.entry_id]["calendar_entity"] = calendar_entity
    hass.data[DOMAIN][entry.entry_id]["add_calendar_entities"] = async_add_entities
    async_add_entities([calendar_entity])

class HygieneCalendar(CalendarEntity):
    def __init__(self, name, unique_id):
        self._name = name
        self._unique_id = unique_id
        self._attr_has_entity_name = True
        self._events = []

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def event(self) -> CalendarEvent | None:
        """Return the current or next upcoming event."""
        now = dt_util.utcnow()

        # Filter for current or future events
        upcoming_events = sorted(
            [
                e for e in self._events
                if e.start and e.end and dt_util.as_utc(e.end) > now
            ],
            key=lambda e: dt_util.as_utc(e.start)
        )

        for e in upcoming_events:
            if dt_util.as_utc(e.start) <= now <= dt_util.as_utc(e.end):
                _LOGGER.debug("📅 Event happening: uid=%s start=%s, end=%s, summary=%s", e.uid, e.start, e.end, e.summary)
                return e  # Current ongoing event
                
        return upcoming_events[0] if upcoming_events else None


    @property
    def supported_features(self) -> int:
        """Flag supported features."""
        return 0  # CREATE_EVENT + UPDATE_EVENT + DELETE_EVENT

    


    async def async_get_events(
        self,
        hass: HomeAssistant,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
        ) -> list[CalendarEvent]:
            """Return calendar events within a datetime range."""
    
            _LOGGER.debug("Getting events from %s to %s", start_date, end_date)

            start_date = dt_util.as_utc(start_date)
            end_date = dt_util.as_utc(end_date)

            events = [
                e for e in self._events
                if e.start and e.end and e.end > start_date and e.start < end_date
            ]

            # Sort events by start time
            events.sort(key=lambda event: dt_util.as_utc(event.start))

            # Log events individually
            for event in events:
                _LOGGER.debug("📅 Event in range: start=%s, end=%s, summary=%s", event.start, event.end, event.summary)

            return events


    async def async_create_event(self, **kwargs: any) -> None:
        """Create a new hygiene event."""
        
        if "dtstart" in kwargs:
            kwargs["start"] = kwargs.pop("dtstart")

        if "dtend" in kwargs:
            kwargs["end"] = kwargs.pop("dtend")

        if "uid" not in kwargs:
            kwargs["uid"] = str(uuid.uuid4())

        # Create event WITHOUT uid first
        event = CalendarEvent(
            summary=kwargs.get("summary", ""),
            start=kwargs.get("start"),
            end=kwargs.get("end"),
            description=kwargs.get("description", ""),
            location=kwargs.get("location", "")
        )

        # Then assign UID manually
        event.uid = kwargs["uid"]

        _LOGGER.debug("📅 Created CalendarEvent with data: %s", vars(event))
        self._events.append(event)
        self.async_write_ha_state()

    async def async_update_event(
        self,
        uid: str,
        event: dict[str, any],
        recurrence_id: str | None = None,
        recurrence_range: str | None = None,
    ) -> None:
        """Update an existing event."""
        for existing_event in self._events:
            if existing_event.uid == uid:
                existing_event.summary = event.get("summary", "")
                existing_event.start = event.get("start")
                existing_event.end = event.get("end")
                existing_event.description = event.get("description", "")
                existing_event.location = event.get("location", "")
                self.async_write_ha_state()
                return

    async def async_delete_event(
        self,
        uid: str,
        recurrence_id: str | None = None,
        recurrence_range: str | None = None,
    ) -> None:
        """Delete an event from the calendar."""
        self._events = [e for e in self._events if e.uid != uid]
        self.async_write_ha_state()
