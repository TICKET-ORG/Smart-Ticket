from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.mock.repository import DemoRepository

client = TestClient(app)


def test_operator_dashboard_renders_assigned_venues() -> None:
    response = client.get("/operator/dashboard")

    assert response.status_code == 200
    assert "you are on the gate" in response.text
    assert "Senja Kala — Album Release Night" in response.text
    assert "Ruang Reka: Design &amp; Technology Forum" in response.text
    assert "Pasar Kreatif" not in response.text
    assert "Sample history · not produced by a live scan" in response.text
    assert "set-cookie" not in response.headers


def test_operator_scanner_renders_both_stages() -> None:
    response = client.get("/operator/scanner")

    assert response.status_code == 200
    assert "One pass at a time." in response.text
    assert "Read the pass" in response.text
    assert "Verify the holder" in response.text
    assert "data-gate-capture" in response.text
    assert "Verification is not connected." in response.text


def test_scanner_lookup_shows_demo_pass_without_consuming_it() -> None:
    response = client.get("/operator/scanner", params={"token": "ST-2026-4F8K-91QD"})

    assert response.status_code == 200
    assert "Pass found" in response.text
    assert "Alya Prameswari" in response.text
    assert "the pass is not consumed" in response.text
    assert "the pass was left untouched" in response.text


def test_scanner_lookup_is_case_insensitive() -> None:
    response = client.get("/operator/scanner", params={"token": "st-2026-7m2p-38vx"})

    assert response.status_code == 200
    assert "Ruang Reka" in response.text
    assert "No demo pass matches" not in response.text


def test_scanner_unknown_token_shows_warning() -> None:
    response = client.get("/operator/scanner", params={"token": "ST-2026-0000-0000"})

    assert response.status_code == 200
    assert "No demo pass matches" in response.text
    assert "Pass found" not in response.text


def test_scanner_flags_a_used_pass() -> None:
    response = client.get("/operator/scanner", params={"token": "ST-2026-1T9A-64HN"})

    assert response.status_code == 200
    assert "Do not admit it again." in response.text


def test_scanner_ignores_unassigned_event_filter() -> None:
    response = client.get("/operator/scanner", params={"event": "evt-pasar-kreatif"})

    assert response.status_code == 200
    assert 'value="evt-pasar-kreatif" selected' not in response.text


def test_operator_history_lists_every_scan() -> None:
    response = client.get("/operator/history")

    assert response.status_code == 200
    assert "What happened at the gate." in response.text
    assert response.text.count("Sample record") >= 5
    assert "All venues" in response.text


def test_operator_history_filters_by_event() -> None:
    response = client.get("/operator/history", params={"event": "evt-ruang-reka"})

    assert response.status_code == 200
    assert "Raka Pratama" in response.text
    assert "Alya Prameswari" not in response.text


def test_operator_history_falls_back_for_unassigned_event() -> None:
    response = client.get("/operator/history", params={"event": "evt-pasar-kreatif"})

    assert response.status_code == 200
    assert "Alya Prameswari" in response.text
    assert 'aria-current="true"' in response.text
    assert "All venues" in response.text


def test_operator_routes_are_demo_only(monkeypatch) -> None:
    monkeypatch.setattr(settings, "demo_mode", False)

    for path in ("/operator/dashboard", "/operator/scanner", "/operator/history"):
        assert client.get(path).status_code == 404, path


def test_repository_operator_events_exclude_free_entry_market() -> None:
    repository = DemoRepository()
    ids = [event.id for event in repository.operator_events()]

    assert ids == ["evt-malam-puisi", "evt-senja-kala", "evt-ruang-reka"]
    assert "evt-pasar-kreatif" not in ids


def test_repository_checkin_summary_counts_results() -> None:
    repository = DemoRepository()

    overall = repository.checkin_summary()
    assert overall.total == 5
    assert overall.granted == 3
    assert overall.denied == 2
    assert overall.grant_rate == 60

    senja = repository.checkin_summary("evt-senja-kala")
    assert (senja.granted, senja.denied) == (2, 1)

    assert repository.checkin_summary("evt-nada-timur").total == 0
    assert repository.checkin_summary("evt-nada-timur").grant_rate == 0


def test_repository_checkin_log_views_join_events() -> None:
    repository = DemoRepository()
    views = repository.checkin_log_views(limit=2)

    assert len(views) == 2
    assert all(view.event is not None for view in views)
    assert views[0].time_label.count(":") == 2

    filtered = repository.checkin_log_views(event_id="evt-ruang-reka")
    assert {view.event.id for view in filtered} == {"evt-ruang-reka"}


def test_repository_ticket_lookup_by_code_does_not_mutate_status() -> None:
    repository = DemoRepository()
    view = repository.ticket_view_by_code("ST-2026-4F8K-91QD")

    assert view is not None
    assert view.is_active
    assert repository.ticket_view_by_code("   ") is None
    assert repository.ticket_view_by_code("ST-NOPE") is None
