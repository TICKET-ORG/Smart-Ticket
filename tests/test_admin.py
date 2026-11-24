from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.mock.repository import DemoRepository

client = TestClient(app)


def test_admin_dashboard_renders_programme_totals() -> None:
    response = client.get("/admin/dashboard")

    assert response.status_code == 200
    assert "The whole programme, in one place." in response.text
    assert "Records on file" in response.text
    assert "Latest gate activity" in response.text
    assert "Sample history · not produced by a live scan" in response.text
    assert "set-cookie" not in response.headers


def test_admin_dashboard_links_only_to_implemented_pages() -> None:
    response = client.get("/admin/dashboard")

    assert 'href="/admin/events#new-event"' in response.text
    assert 'href="/admin/registrations"' in response.text
    assert "/cv-lab" not in response.text


def test_admin_events_lists_every_event() -> None:
    response = client.get("/admin/events")

    assert response.status_code == 200
    assert "The programme." in response.text
    assert "Pasar Kreatif Minggu Pagi" in response.text
    assert "Konser Filharmoni Nusantara" in response.text
    assert response.text.count('class="row-title"') >= 6


def test_admin_events_form_is_presentation_only() -> None:
    repository = DemoRepository()
    before = len(repository.list_events())

    response = client.post(
        "/admin/events",
        data={
            "title": "Test Event",
            "location": "Somewhere",
            "description": "A description",
            "start_at": "2026-12-01T19:00",
            "end_at": "2026-12-01T22:00",
            "capacity": "250",
        },
    )

    assert response.status_code == 200
    assert "Nothing was saved and no event was created." in response.text
    assert 'value="Test Event"' in response.text
    assert 'value="Somewhere"' in response.text
    assert 'value="250"' in response.text
    assert "Test Event" not in client.get("/admin/events").text
    assert len(repository.list_events()) == before


def test_admin_registrations_lists_every_row() -> None:
    response = client.get("/admin/registrations")

    assert response.status_code == 200
    assert "Who is coming." in response.text
    assert "Sample records · no registration was created here" in response.text
    assert response.text.count('class="row-sub"') >= 16


def _table_body(html: str) -> str:
    """Only the rows, so filter chips and headings do not affect assertions."""

    start = html.index("<tbody>")
    return html[start : html.index("</tbody>", start)]


def test_admin_registrations_filters_by_event() -> None:
    response = client.get("/admin/registrations", params={"event": "evt-malam-puisi"})
    body = _table_body(response.text)

    assert response.status_code == 200
    assert "Malam Puisi: Suara dari Tepi" in body
    assert "Konser Filharmoni Nusantara" not in body
    assert body.count("<tr>") == 3


def test_admin_registrations_filters_by_status() -> None:
    response = client.get("/admin/registrations", params={"status": "cancelled"})

    assert response.status_code == 200
    assert "Raka Pratama" in response.text
    assert "Bimo Saputra" in response.text
    assert "badge--success" not in response.text


def test_admin_registrations_falls_back_for_unassigned_event() -> None:
    response = client.get("/admin/registrations", params={"event": "evt-pasar-kreatif"})

    assert response.status_code == 200
    assert "Alya Prameswari" in response.text
    assert "All venues" in response.text


def test_admin_registrations_ignores_unknown_status() -> None:
    filtered = client.get("/admin/registrations", params={"status": "BOGUS"})
    unfiltered = client.get("/admin/registrations")

    assert filtered.status_code == 200
    assert filtered.text.count("<tr>") == unfiltered.text.count("<tr>")
    assert "Any status" in filtered.text


def test_admin_routes_are_demo_only(monkeypatch) -> None:
    monkeypatch.setattr(settings, "demo_mode", False)

    for path in ("/admin/dashboard", "/admin/events", "/admin/registrations"):
        assert client.get(path).status_code == 404, path


def test_repository_admin_summary_counts_records() -> None:
    summary = DemoRepository().admin_summary()

    assert summary.events == 6
    assert summary.registrations == 16
    assert summary.confirmed == 14
    assert summary.cancelled == 2
    assert summary.passes == 7
    assert summary.granted_entries == 3
    assert summary.cancelled_rate == 12


def test_repository_admin_registration_views_join_holder_and_pass() -> None:
    repository = DemoRepository()
    views = repository.all_registration_views()

    assert len(views) == 16
    assert all(view.user.role == "participant" for view in views)
    assert all(view.event is not None for view in views)
    assert [view.created_at for view in views] == sorted(
        (view.created_at for view in views), reverse=True
    )

    confirmed = repository.all_registration_views(status="confirmed")
    assert len(confirmed) == 14
    assert all(view.status == "CONFIRMED" for view in confirmed)

    assert repository.all_registration_views(event_id="evt-nada-timur") != []
    assert repository.all_registration_views(event_id="evt-pasar-kreatif") == []


def test_repository_admin_programme_helpers() -> None:
    repository = DemoRepository()

    upcoming = repository.upcoming_events(limit=3)
    assert len(upcoming) == 3
    assert [event.start_at for event in upcoming] == sorted(event.start_at for event in upcoming)

    filterable = repository.events_with_registrations()
    assert "evt-pasar-kreatif" not in {event.id for event in filterable}
    assert len(filterable) == 5

    assert repository.participant_count() == 8
    assert repository.enrolled_profile_count() == 3


def test_expanded_fixtures_keep_the_demo_participant_intact() -> None:
    repository = DemoRepository()

    tickets = repository.list_ticket_views_for("usr-participant")
    assert [ticket.id for ticket in tickets] == [
        "tkt-senja-kala",
        "tkt-ruang-reka",
        "tkt-nada-timur",
    ]
    assert repository.face_profile_for("usr-participant").sample_count == 9
