from fastapi.testclient import TestClient

from app.main import app
from app.mock.repository import DemoRepository

client = TestClient(app)


def test_catalog_lists_every_event() -> None:
    response = client.get("/events")

    assert response.status_code == 200
    assert "The calendar." in response.text
    assert "Pasar Kreatif" in response.text
    assert "06 / 06 events" in response.text


def test_catalog_filters_by_category() -> None:
    response = client.get("/events", params={"category": "Concert"})

    assert response.status_code == 200
    assert "Senja Kala" in response.text
    assert "Ruang Reka" not in response.text
    assert "01 / 06 events" in response.text


def test_catalog_filters_by_query() -> None:
    response = client.get("/events", params={"q": "surabaya"})

    assert response.status_code == 200
    assert "Nada Timur" in response.text
    assert "Senja Kala" not in response.text


def test_catalog_empty_state_when_nothing_matches() -> None:
    response = client.get("/events", params={"q": "no-such-event"})

    assert response.status_code == 200
    assert "Nothing on the calendar matches that." in response.text


def test_event_details_renders_schedule_and_entry_steps() -> None:
    response = client.get("/events/evt-senja-kala")

    assert response.status_code == 200
    assert "Senja Kala — Album Release Night" in response.text
    assert "Registration opens" in response.text
    assert "Face matched" in response.text
    assert "Also on the calendar" in response.text


def test_event_details_hides_registration_when_sold_out() -> None:
    response = client.get("/events/evt-malam-puisi")

    assert response.status_code == 200
    assert "Sold out" in response.text
    assert "Register &amp; enroll" not in response.text


def test_unknown_event_returns_designed_404() -> None:
    response = client.get("/events/evt-does-not-exist")

    assert response.status_code == 404
    assert "This door doesn't open." in response.text


def test_search_events_matches_venue_and_city() -> None:
    repository = DemoRepository()

    assert [event.id for event in repository.search_events(query="graha")] == ["evt-senja-kala"]
    assert repository.search_events(query="no-such-event") == []
    assert len(repository.search_events(category="Concert")) == 1


def test_related_events_prefer_same_category() -> None:
    repository = DemoRepository()
    related = repository.related_events("evt-senja-kala", limit=3)

    assert len(related) == 3
    assert "evt-senja-kala" not in [event.id for event in related]
