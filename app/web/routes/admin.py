"""Admin overview, event management, and the registration roster.

Interface only. The event form is presentation-only: submitting it re-renders
the page with a demo notice and writes nothing, because there is no event
service to write to yet. Every route is gated on ``DEMO_MODE`` until a session
guard exists.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from app.mock.fixtures import DemoUser
from app.mock.repository import DemoRepository
from app.web.demo import require_demo
from app.web.deps import RepositoryDep
from app.web.templating import render

router = APIRouter(prefix="/admin", tags=["admin"])

EVENT_FORM_NOTICE = (
    "Demo mode — events are not connected yet. Nothing was saved and no event was created."
)

EVENT_FORM_FIELDS = ("title", "location", "description", "start_at", "end_at", "capacity")

REGISTRATION_STATUSES = ("CONFIRMED", "CANCELLED")


def _admin(repository: DemoRepository) -> DemoUser:
    user = repository.user_for_role("admin")
    if user is None:  # pragma: no cover - fixtures always provide one
        raise HTTPException(status_code=404, detail="Not found")
    return user


def _shell(user: DemoUser, *, title: str, kicker: str, page: str) -> dict[str, object]:
    return {
        "user": user,
        "nav_role": "admin",
        "page_title": title,
        "page_kicker": kicker,
        "active_page": page,
    }


def _empty_form() -> dict[str, str]:
    return {field: "" for field in EVENT_FORM_FIELDS}


def _events_context(
    repository: DemoRepository,
    user: DemoUser,
    *,
    form: dict[str, str],
    notice: str | None,
) -> dict[str, object]:
    context = _shell(user, title="Events", kicker="Admin", page="events")
    context.update(
        {
            "events": repository.list_events(),
            "form": form,
            "notice": notice,
            "enrolled_profiles": repository.enrolled_profile_count(),
        }
    )
    return context


@router.get("/dashboard")
def admin_dashboard(request: Request, repository: RepositoryDep):
    require_demo()
    user = _admin(repository)

    context = _shell(user, title="Overview", kicker="Admin", page="dashboard")
    context.update(
        {
            "summary": repository.admin_summary(),
            "upcoming": repository.upcoming_events(limit=3),
            "recent_logs": repository.checkin_log_views(limit=6),
            "enrolled_profiles": repository.enrolled_profile_count(),
            "participant_count": repository.participant_count(),
            "event_count": len(repository.list_events()),
        }
    )
    return render(request, "admin/dashboard.html", context)


@router.get("/events")
def admin_events(request: Request, repository: RepositoryDep):
    require_demo()
    user = _admin(repository)

    context = _events_context(repository, user, form=_empty_form(), notice=None)
    return render(request, "admin/events.html", context)


@router.post("/events")
async def admin_events_submit(request: Request, repository: RepositoryDep):
    require_demo()
    user = _admin(repository)

    form = await request.form()
    payload = {field: str(form.get(field, "")) for field in EVENT_FORM_FIELDS}

    context = _events_context(repository, user, form=payload, notice=EVENT_FORM_NOTICE)
    return render(request, "admin/events.html", context)


@router.get("/registrations")
def admin_registrations(
    request: Request,
    repository: RepositoryDep,
    event: str = "",
    status: str = "",
):
    require_demo()
    user = _admin(repository)

    filterable = repository.events_with_registrations()
    selected = repository.get_event(event) if event else None
    if selected is not None and selected.id not in {item.id for item in filterable}:
        selected = None

    wanted = status.strip().upper()
    if wanted not in REGISTRATION_STATUSES:
        wanted = ""

    rows = repository.all_registration_views(
        event_id=selected.id if selected else None,
        status=wanted or None,
    )

    context = _shell(user, title="Registrations", kicker="Admin", page="registrations")
    context.update(
        {
            "events": filterable,
            "event": selected,
            "status": wanted,
            "rows": rows,
            "confirmed_count": sum(1 for row in rows if row.status == "CONFIRMED"),
            "cancelled_count": sum(1 for row in rows if row.status == "CANCELLED"),
            "summary": repository.admin_summary(),
        }
    )
    return render(request, "admin/registrations.html", context)
