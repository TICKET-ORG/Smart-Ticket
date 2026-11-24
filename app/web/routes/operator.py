"""Operator dashboard, gate scanner, and scan history.

Interface only. The scanner renders a real camera preview and can look up a
demo token against the fixture repository, but it never produces a verification
verdict: the face step ends in an explicit "not connected" state and no pass is
consumed. Every route is gated on ``DEMO_MODE`` until a session guard exists.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from app.mock.fixtures import DemoUser
from app.mock.repository import DemoRepository
from app.web.demo import require_demo
from app.web.deps import RepositoryDep
from app.web.templating import render

router = APIRouter(prefix="/operator", tags=["operator"])


def _operator(repository: DemoRepository) -> DemoUser:
    user = repository.user_for_role("operator")
    if user is None:  # pragma: no cover - fixtures always provide one
        raise HTTPException(status_code=404, detail="Not found")
    return user


def _shell(user: DemoUser, *, title: str, kicker: str, page: str) -> dict[str, object]:
    return {
        "user": user,
        "nav_role": "operator",
        "page_title": title,
        "page_kicker": kicker,
        "active_page": page,
    }


@router.get("/dashboard")
def operator_dashboard(request: Request, repository: RepositoryDep):
    require_demo()
    user = _operator(repository)
    events = repository.operator_events()

    context = _shell(user, title="Overview", kicker="Operator", page="dashboard")
    context.update(
        {
            "events": events,
            "summary": repository.checkin_summary(),
            "recent_logs": repository.checkin_log_views(limit=6),
        }
    )
    return render(request, "operator/dashboard.html", context)


@router.get("/scanner")
def operator_scanner(request: Request, repository: RepositoryDep, token: str = "", event: str = ""):
    require_demo()
    user = _operator(repository)

    selected = repository.get_event(event) if event else None
    allowed = repository.operator_events()
    if selected is not None and selected not in allowed:
        selected = None

    pass_view = repository.ticket_view_by_code(token) if token.strip() else None
    lookup_failed = bool(token.strip()) and pass_view is None

    context = _shell(user, title="Scanner", kicker="Operator", page="scanner")
    context.update(
        {
            "events": allowed,
            "event": selected,
            "token": token,
            "pass_view": pass_view,
            "lookup_failed": lookup_failed,
        }
    )
    return render(request, "operator/scanner.html", context)


@router.get("/history")
def operator_history(request: Request, repository: RepositoryDep, event: str = ""):
    require_demo()
    user = _operator(repository)
    events = repository.operator_events()

    selected = repository.get_event(event) if event else None
    if selected is not None and selected not in events:
        selected = None

    event_id = selected.id if selected else None
    logs = repository.checkin_log_views(event_id=event_id)

    context = _shell(user, title="History", kicker="Operator", page="history")
    context.update(
        {
            "events": events,
            "event": selected,
            "logs": logs,
            "summary": repository.checkin_summary(event_id),
        }
    )
    return render(request, "operator/history.html", context)
