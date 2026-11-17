from fastapi.testclient import TestClient

from app.main import app
from app.mock.repository import DemoRepository

client = TestClient(app)


def test_landing_page_renders() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "Your face is the" in response.text
    assert "Senja Kala" in response.text
    assert "Pasar Kreatif" not in response.text


def test_styleguide_renders() -> None:
    response = client.get("/dev/styleguide")

    assert response.status_code == 200
    assert "Design system" in response.text
    assert "Instrument Serif" in response.text


def test_not_found_uses_designed_page() -> None:
    response = client.get("/does-not-exist")

    assert response.status_code == 404
    assert "This door doesn't open." in response.text


def test_health_endpoint() -> None:
    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_static_assets_are_served() -> None:
    assets = [
        "/static/css/tokens.css",
        "/static/css/base.css",
        "/static/css/layout.css",
        "/static/css/components.css",
        "/static/css/pages/landing.css",
        "/static/js/app.js",
        "/static/js/core/nav.js",
        "/static/images/icons.svg",
        "/static/images/qr-demo.svg",
        "/static/vendor/fonts/instrument-sans-latin.woff2",
        "/static/vendor/fonts/instrument-serif-latin.woff2",
    ]

    for asset in assets:
        assert client.get(asset).status_code == 200, asset


def test_featured_events_are_curated_not_chronological() -> None:
    repository = DemoRepository()
    featured_ids = [event.id for event in repository.featured_events()]

    assert featured_ids == ["evt-senja-kala", "evt-ruang-reka", "evt-nada-timur"]
    assert featured_ids != [event.id for event in repository.list_events(limit=3)]
