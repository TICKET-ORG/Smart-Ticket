"""In-memory repository used while the backend data layer is being built.

Swap this class for the real repository/service in a later PR. Page routes only
depend on the methods declared here, not on the fixture implementation.
"""

from __future__ import annotations

from datetime import datetime

from app.mock.fixtures import (
    DemoCheckinLog,
    DemoCheckinLogView,
    DemoCheckinSummary,
    DemoEvent,
    DemoFaceProfile,
    DemoRegistration,
    DemoRegistrationView,
    DemoTicket,
    DemoTicketView,
    DemoUser,
    demo_checkin_logs,
    demo_events,
    demo_face_profiles,
    demo_registrations,
    demo_tickets,
    demo_users,
)

FEATURED_EVENT_IDS = ("evt-senja-kala", "evt-ruang-reka", "evt-nada-timur")

# The demo operator is assigned to the venues with a gate: no free-entry market.
OPERATOR_EVENT_IDS = ("evt-senja-kala", "evt-ruang-reka", "evt-malam-puisi")


class DemoRepository:
    def __init__(self) -> None:
        self._events = sorted(demo_events(), key=lambda event: event.start_at)
        self._tickets = demo_tickets()
        self._users = {user.id: user for user in demo_users()}
        self._checkin_logs = demo_checkin_logs()
        self._face_profiles = {profile.user_id: profile for profile in demo_face_profiles()}
        self._registrations = demo_registrations()

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

    def get_user(self, user_id: str) -> DemoUser | None:
        return self._users.get(user_id)

    def face_profile_for(self, user_id: str) -> DemoFaceProfile | None:
        return self._face_profiles.get(user_id)

    def list_tickets_for(self, user_id: str) -> list[DemoTicket]:
        return [ticket for ticket in self._tickets if ticket.user_id == user_id]

    def ticket_by_id(self, ticket_id: str) -> DemoTicket | None:
        return next((ticket for ticket in self._tickets if ticket.id == ticket_id), None)

    def _join_ticket(self, ticket: DemoTicket) -> DemoTicketView | None:
        event = self.get_event(ticket.event_id)
        user = self.get_user(ticket.user_id)
        if event is None or user is None:
            return None

        return DemoTicketView(
            id=ticket.id,
            code=ticket.code,
            event=event,
            user=user,
            status=ticket.status,
            issued_at=ticket.issued_at,
            used_at=ticket.used_at,
            seat=ticket.seat,
        )

    def ticket_view(self, ticket_id: str) -> DemoTicketView | None:
        ticket = self.ticket_by_id(ticket_id)
        return self._join_ticket(ticket) if ticket else None

    def list_ticket_views_for(self, user_id: str) -> list[DemoTicketView]:
        """Active passes first, then the most recent events."""

        views = [self._join_ticket(ticket) for ticket in self.list_tickets_for(user_id)]
        tickets = [view for view in views if view is not None]
        tickets.sort(key=lambda view: (not view.is_active, view.event.start_at))
        return tickets

    def next_ticket_for(self, user_id: str) -> DemoTicketView | None:
        """The soonest active pass for an event that has not started yet."""

        now = datetime.now()
        upcoming = [
            view
            for view in self.list_ticket_views_for(user_id)
            if view.is_active and view.event.start_at >= now
        ]
        return upcoming[0] if upcoming else None

    def list_registration_views_for(self, user_id: str) -> list[DemoRegistrationView]:
        views: list[DemoRegistrationView] = []
        for registration in self._registrations:
            if registration.user_id != user_id:
                continue
            event = self.get_event(registration.event_id)
            if event is None:
                continue
            ticket = self.ticket_view(registration.ticket_id) if registration.ticket_id else None
            views.append(
                DemoRegistrationView(
                    id=registration.id,
                    status=registration.status,
                    created_at=registration.created_at,
                    event=event,
                    ticket=ticket,
                )
            )

        views.sort(key=lambda view: view.event.start_at)
        return views

    def list_registrations_for(self, user_id: str) -> list[DemoRegistration]:
        return [
            registration for registration in self._registrations if registration.user_id == user_id
        ]

    def list_checkin_logs(self, limit: int | None = None) -> list[DemoCheckinLog]:
        logs = sorted(self._checkin_logs, key=lambda log: log.created_at, reverse=True)
        return logs[:limit] if limit else logs

    # Operator -----------------------------------------------------

    def operator_events(self) -> list[DemoEvent]:
        """Events the demo operator is allowed to staff, soonest first."""

        events = [self.get_event(event_id) for event_id in OPERATOR_EVENT_IDS]
        return sorted(
            (event for event in events if event is not None),
            key=lambda event: event.start_at,
        )

    def checkin_log_views(
        self,
        *,
        event_id: str | None = None,
        limit: int | None = None,
    ) -> list[DemoCheckinLogView]:
        logs = self.list_checkin_logs()
        if event_id:
            logs = [log for log in logs if log.event_id == event_id]

        views = [
            DemoCheckinLogView(
                id=log.id,
                participant=log.participant,
                result=log.result,
                reason=log.reason,
                created_at=log.created_at,
                operator=log.operator,
                event=self.get_event(log.event_id) if log.event_id else None,
            )
            for log in logs
        ]
        return views[:limit] if limit else views

    def checkin_summary(self, event_id: str | None = None) -> DemoCheckinSummary:
        logs = self.list_checkin_logs()
        if event_id:
            logs = [log for log in logs if log.event_id == event_id]

        granted = sum(1 for log in logs if log.result == "GRANTED")
        return DemoCheckinSummary(granted=granted, denied=len(logs) - granted)

    def ticket_view_by_code(self, code: str) -> DemoTicketView | None:
        """Demo lookup for the manual-entry token field.

        This reads the same fixtures the participant pass page renders. It is
        not a check-in: nothing is consumed and no verification runs.
        """

        needle = code.strip().upper()
        if not needle:
            return None

        ticket = next(
            (item for item in self._tickets if item.code.upper() == needle),
            None,
        )
        return self._join_ticket(ticket) if ticket else None
