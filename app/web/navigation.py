"""Role-aware navigation for the signed-in application shell.

The dashboard routes are still interface-only, so the role switcher is a demo
control, not an authorization boundary. When the session layer lands, the
current role must come from the session and this module keeps only the labels
and paths.
"""

from __future__ import annotations

PARTICIPANT_NAV = (
    {
        "label": "Overview",
        "href": "/participant/dashboard",
        "page": "dashboard",
        "icon": "activity",
    },
    {
        "label": "Enrollment",
        "href": "/participant/enrollment",
        "page": "enrollment",
        "icon": "scan-face",
    },
    {
        "label": "Tickets",
        "href": "/participant/tickets",
        "page": "tickets",
        "icon": "ticket",
    },
)

OPERATOR_NAV = (
    {
        "label": "Overview",
        "href": "/operator/dashboard",
        "page": "dashboard",
        "icon": "activity",
    },
    {
        "label": "Scanner",
        "href": "/operator/scanner",
        "page": "scanner",
        "icon": "scan-face",
    },
    {
        "label": "History",
        "href": "/operator/history",
        "page": "history",
        "icon": "clock",
    },
)

ROLE_NAV = {
    "participant": PARTICIPANT_NAV,
    "operator": OPERATOR_NAV,
}

ROLE_LABELS = {
    "participant": "Participant",
    "operator": "Operator",
    "admin": "Admin",
}

# Roles that have pages in this build. The others are shown in the switcher as
# disabled so the demo never links to a route that does not exist yet.
DEMO_ROLES = (
    {
        "id": "participant",
        "label": ROLE_LABELS["participant"],
        "description": "Attend events",
        "href": "/participant/dashboard",
        "available": True,
    },
    {
        "id": "operator",
        "label": ROLE_LABELS["operator"],
        "description": "Check passes at the gate",
        "href": "/operator/dashboard",
        "available": True,
    },
    {
        "id": "admin",
        "label": ROLE_LABELS["admin"],
        "description": "Manage events and people",
        "href": None,
        "available": False,
    },
)


def nav_for(role: str) -> tuple[dict[str, str], ...]:
    return ROLE_NAV.get(role, ())


def role_label(role: str | None) -> str:
    return ROLE_LABELS.get(role or "", "Guest")
