"""In-memory repository used while the backend data layer is being built.

Swap this class for the real repository/service in a later PR. Page routes only
depend on the methods declared here, not on the fixture implementation.
"""

from __future__ import annotations

from app.mock.fixtures import (
    DemoCheckinLog,
    DemoEvent,
    DemoTicket,
    DemoUser,
    demo_checkin_logs,
    demo_events,
    demo_tickets,
    demo_users,
)

FEATURED_EVENT_IDS = ("evt-senja-kala", "evt-ruang-reka", "evt-nada-timur")


class DemoRepository:
    def __init__(self) -> None:
        self._events = sorted(demo_events(), key=lambda event: event.start_at)
        self._tickets = demo_tickets()
        self._users = {user.id: user for user in demo_users()}
        self._checkin_logs = demo_checkin_logs()

    def list_events(self, limit: int | None = None) -> list[DemoEvent]:
        events = list(self._events)
        return events[:limit] if limit else events

    def featured_events(self, limit: int = 3) -> list[DemoEvent]:
        """A curated landing selection, not simply the next three dates."""

        events = {event.id: event for event in self._events}
        ordered = [events[event_id] for event_id in FEATURED_EVENT_IDS if event_id in events]
        return ordered[:limit]

    def get_event(self, event_id: str) -> DemoEvent | None:
        return next((event for event in self._events if event.id == event_id), None)

    def list_categories(self) -> list[str]:
        return sorted({event.category for event in self._events})

    def search_events(self, query: str = "", category: str = "") -> list[DemoEvent]:
        """Filter the catalog. Live data will move this into the query layer."""

        needle = query.strip().lower()
        wanted = category.strip().lower()

        events = self._events
        if wanted:
            events = [event for event in events if event.category.lower() == wanted]

        if needle:
            events = [
                event
                for event in events
                if needle
                in " ".join(
                    (
                        event.title,
                        event.description,
                        event.category,
                        event.location,
                        event.city,
                    )
                ).lower()
            ]

        return list(events)

    def related_events(self, event_id: str, limit: int = 3) -> list[DemoEvent]:
        """Prefer the same category, then fill with the nearest dates."""

        current = self.get_event(event_id)
        others = [event for event in self._events if event.id != event_id]
        if current is not None:
            others.sort(key=lambda event: (event.category != current.category, event.start_at))
        return others[:limit]

    def user_for_role(self, role: str) -> DemoUser | None:
        return next((user for user in self._users.values() if user.role == role), None)

    def list_tickets_for(self, user_id: str) -> list[DemoTicket]:
        return [ticket for ticket in self._tickets if ticket.user_id == user_id]

    def list_checkin_logs(self, limit: int | None = None) -> list[DemoCheckinLog]:
        logs = sorted(self._checkin_logs, key=lambda log: log.created_at, reverse=True)
        return logs[:limit] if limit else logs
