from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.mock.repository import DemoRepository

client = TestClient(app)

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def test_participant_dashboard_renders_overview() -> None:
    response = client.get("/participant/dashboard")

    assert response.status_code == 200
    assert "Welcome back, Alya." in response.text
    assert "Profile verified" in response.text
    assert "Senja Kala — Album Release Night" in response.text
    assert "Demo mode — role simulated." in response.text
    assert "set-cookie" not in response.headers


def test_participant_enrollment_renders_all_poses() -> None:
    response = client.get("/participant/enrollment")

    assert response.status_code == 200
    assert "Nine frames. One profile." in response.text
    assert response.text.count('class="pose-list__item"') == 9
    assert "data-camera-capture" in response.text
    assert "Nothing leaves this browser." in response.text


def test_participant_tickets_lists_every_pass() -> None:
    response = client.get("/participant/tickets")

    assert response.status_code == 200
    assert "Your passes." in response.text
    assert "Senja Kala — Album Release Night" in response.text
    assert "Ruang Reka: Design &amp; Technology Forum" in response.text
    assert "Nada Timur Festival 2026" in response.text
    assert "ACTIVE" in response.text
    assert "USED" in response.text


def test_ticket_detail_shows_qr_and_manual_token() -> None:
    response = client.get("/participant/tickets/tkt-senja-kala")

    assert response.status_code == 200
    assert "Admit one" in response.text
    assert "ST-2026-4F8K-91QD" in response.text
    assert "/participant/tickets/tkt-senja-kala/qr.png" in response.text
    assert "A match consumes the pass." in response.text


def test_used_ticket_detail_is_flagged() -> None:
    response = client.get("/participant/tickets/tkt-nada-timur")

    assert response.status_code == 200
    assert "It cannot be scanned again." in response.text
    assert "pass-qr--used" in response.text


def test_unknown_ticket_returns_404() -> None:
    response = client.get("/participant/tickets/tkt-does-not-exist")

    assert response.status_code == 404


def test_ticket_qr_returns_png() -> None:
    response = client.get("/participant/tickets/tkt-senja-kala/qr.png")

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert response.headers["cache-control"] == "no-store"
    assert response.content.startswith(PNG_SIGNATURE)


def test_participant_routes_are_demo_only(monkeypatch) -> None:
    monkeypatch.setattr(settings, "demo_mode", False)

    paths = [
        "/participant/dashboard",
        "/participant/enrollment",
        "/participant/tickets",
        "/participant/tickets/tkt-senja-kala",
        "/participant/tickets/tkt-senja-kala/qr.png",
    ]

    for path in paths:
        assert client.get(path).status_code == 404, path


def test_repository_joins_ticket_event_and_holder() -> None:
    repository = DemoRepository()
    ticket = repository.ticket_view("tkt-senja-kala")

    assert ticket is not None
    assert ticket.event.id == "evt-senja-kala"
    assert ticket.user.name == "Alya Prameswari"
    assert ticket.is_active


def test_repository_orders_active_passes_before_used() -> None:
    repository = DemoRepository()
    tickets = repository.list_ticket_views_for("usr-participant")

    assert [ticket.id for ticket in tickets] == [
        "tkt-senja-kala",
        "tkt-ruang-reka",
        "tkt-nada-timur",
    ]
    assert [ticket.is_active for ticket in tickets] == [True, True, False]


def test_repository_next_ticket_is_the_soonest_active_event() -> None:
    repository = DemoRepository()

    assert repository.next_ticket_for("usr-participant").id == "tkt-senja-kala"
    assert repository.next_ticket_for("usr-operator") is None


def test_repository_registration_views_include_tickets() -> None:
    repository = DemoRepository()
    registrations = repository.list_registration_views_for("usr-participant")

    assert [registration.event.id for registration in registrations] == [
        "evt-senja-kala",
        "evt-ruang-reka",
        "evt-nada-timur",
    ]
    assert all(registration.ticket is not None for registration in registrations)
    assert registrations[0].ticket_status == "ACTIVE"
    assert registrations[-1].ticket_status == "USED"
