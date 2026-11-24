"""Participant dashboard, enrollment, and ticket screens.

Interface only. The pages render demo data and never claim that an enrollment,
booking, or check-in was completed. Every route is gated on ``DEMO_MODE`` so a
non-demo deployment does not expose panels that have no session guard yet.
"""

from __future__ import annotations

import io

import qrcode
from fastapi import APIRouter, HTTPException, Request, Response

from app.mock.fixtures import DemoUser
from app.mock.repository import DemoRepository
from app.web.demo import require_demo
from app.web.deps import RepositoryDep
from app.web.enrollment import ENROLLMENT_POSES, TARGET_SAMPLES
from app.web.templating import render

router = APIRouter(prefix="/participant", tags=["participant"])


def _guard_demo() -> None:
    require_demo()


def _participant(repository: DemoRepository) -> DemoUser:
    user = repository.user_for_role("participant")
    if user is None:
        raise HTTPException(status_code=404, detail="Not found")
    return user


def _shell(user: DemoUser, *, title: str, kicker: str, page: str) -> dict[str, object]:
    return {
        "user": user,
        "nav_role": "participant",
        "page_title": title,
        "page_kicker": kicker,
        "active_page": page,
    }


def _qr_png(payload: str) -> bytes:
    code = qrcode.QRCode(
        box_size=9,
        border=2,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
    )
    code.add_data(payload)
    code.make(fit=True)

    image = code.make_image(fill_color="#131210", back_color="#fffdf8")
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


@router.get("/dashboard")
def participant_dashboard(request: Request, repository: RepositoryDep):
    _guard_demo()
    user = _participant(repository)
    profile = repository.face_profile_for(user.id)
    tickets = repository.list_ticket_views_for(user.id)

    context = _shell(user, title="Overview", kicker="Participant", page="dashboard")
    context.update(
        {
            "face_profile": profile,
            "sample_count": profile.sample_count if profile else 0,
            "target_samples": TARGET_SAMPLES,
            "tickets": tickets,
            "active_ticket_count": sum(1 for ticket in tickets if ticket.is_active),
            "registrations": repository.list_registration_views_for(user.id),
            "next_ticket": repository.next_ticket_for(user.id),
        }
    )
    return render(request, "participant/dashboard.html", context)


@router.get("/enrollment")
def participant_enrollment(request: Request, repository: RepositoryDep):
    _guard_demo()
    user = _participant(repository)
    profile = repository.face_profile_for(user.id)

    context = _shell(user, title="Face enrollment", kicker="Participant", page="enrollment")
    context.update(
        {
            "face_profile": profile,
            "sample_count": profile.sample_count if profile else 0,
            "poses": ENROLLMENT_POSES,
            "target_samples": TARGET_SAMPLES,
        }
    )
    return render(request, "participant/enrollment.html", context)


@router.get("/tickets")
def participant_tickets(request: Request, repository: RepositoryDep):
    _guard_demo()
    user = _participant(repository)

    context = _shell(user, title="Tickets", kicker="Participant", page="tickets")
    context.update({"tickets": repository.list_ticket_views_for(user.id)})
    return render(request, "participant/tickets.html", context)


@router.get("/tickets/{ticket_id}")
def participant_ticket_detail(request: Request, ticket_id: str, repository: RepositoryDep):
    _guard_demo()
    user = _participant(repository)
    ticket = repository.ticket_view(ticket_id)

    if ticket is None or ticket.user.id != user.id:
        raise HTTPException(status_code=404, detail="Ticket not found")

    context = _shell(user, title="Your pass", kicker="Participant", page="tickets")
    context.update({"ticket": ticket})
    return render(request, "participant/ticket_detail.html", context)


@router.get("/tickets/{ticket_id}/qr.png", include_in_schema=False)
def participant_ticket_qr(ticket_id: str, repository: RepositoryDep):
    _guard_demo()
    user = _participant(repository)
    ticket = repository.ticket_view(ticket_id)

    if ticket is None or ticket.user.id != user.id:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return Response(
        content=_qr_png(ticket.code),
        media_type="image/png",
        headers={"Cache-Control": "no-store"},
    )
