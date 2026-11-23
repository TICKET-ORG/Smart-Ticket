from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_login_and_register_pages_render() -> None:
    login = client.get("/auth/login")
    register = client.get("/auth/register")

    assert login.status_code == 200
    assert "Welcome back" in login.text
    assert register.status_code == 200
    assert "Create your account" in register.text


def test_login_preserves_next_destination() -> None:
    response = client.get("/auth/login", params={"next": "/events/evt-senja-kala"})

    assert response.status_code == 200
    assert "next=/events/evt-senja-kala" in response.text


def test_login_post_is_presentation_only() -> None:
    response = client.post(
        "/auth/login",
        data={"email": "alya@example.com", "password": "secret123"},
    )

    assert response.status_code == 200
    assert "accounts are not connected yet" in response.text
    assert 'value="alya@example.com"' in response.text
    assert "set-cookie" not in response.headers


def test_register_post_is_presentation_only() -> None:
    response = client.post(
        "/auth/register",
        data={
            "name": "Alya Prameswari",
            "email": "alya@example.com",
            "password": "secret123",
            "consent": "on",
        },
    )

    assert response.status_code == 200
    assert "accounts are not connected yet" in response.text
    assert 'value="Alya Prameswari"' in response.text
    assert "set-cookie" not in response.headers
