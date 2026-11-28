"""Isolamento entre usuários: ninguém lê nem altera sessões de outra pessoa."""

import uuid

import pytest
from fastapi.testclient import TestClient

from app.main import app

PASSWORD = "senha-bem-longa-123"


def sign_in(email: str) -> tuple[TestClient, dict[str, str]]:
    """Cria o usuário; devolve um cliente próprio (cookies separados) e o cabeçalho de acesso."""
    client = TestClient(app)
    created = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": PASSWORD, "full_name": email.split("@")[0]},
    )
    assert created.status_code == 201
    token = client.post(
        "/api/v1/auth/login", json={"email": email, "password": PASSWORD}
    ).json()["access_token"]
    return client, {"Authorization": f"Bearer {token}"}


def only_session_id(client: TestClient, headers: dict[str, str]) -> str:
    sessions = client.get("/api/v1/users/me/sessions", headers=headers).json()
    assert len(sessions) == 1
    return sessions[0]["id"]


@pytest.fixture
def two_users(client: TestClient):
    # `client` configura o banco de teste e os overrides; os dois usuários usam clientes próprios.
    return sign_in("ana@exemplo.com"), sign_in("bruno@exemplo.com")


def test_me_returns_only_the_caller(two_users):
    (ana, ana_h), (bruno, bruno_h) = two_users
    assert ana.get("/api/v1/users/me", headers=ana_h).json()["email"] == "ana@exemplo.com"
    assert bruno.get("/api/v1/users/me", headers=bruno_h).json()["email"] == "bruno@exemplo.com"


def test_session_listing_shows_only_own_sessions(two_users):
    (ana, ana_h), (bruno, bruno_h) = two_users
    ana_id = only_session_id(ana, ana_h)
    bruno_id = only_session_id(bruno, bruno_h)
    assert ana_id != bruno_id


def test_cannot_revoke_another_users_session(two_users):
    (ana, ana_h), (bruno, bruno_h) = two_users
    ana_session = only_session_id(ana, ana_h)

    response = bruno.delete(f"/api/v1/users/me/sessions/{ana_session}", headers=bruno_h)
    assert response.status_code == 404

    # A sessão da Ana continua ativa e utilizável.
    assert ana.post("/api/v1/auth/refresh").status_code == 200
    assert only_session_id(ana, ana_h)


def test_foreign_and_nonexistent_sessions_are_indistinguishable(two_users):
    (ana, ana_h), (bruno, bruno_h) = two_users
    foreign = bruno.delete(
        f"/api/v1/users/me/sessions/{only_session_id(ana, ana_h)}", headers=bruno_h
    )
    missing = bruno.delete(f"/api/v1/users/me/sessions/{uuid.uuid4()}", headers=bruno_h)

    assert foreign.status_code == missing.status_code == 404
    assert foreign.json()["code"] == missing.json()["code"]
    assert foreign.json()["detail"] == missing.json()["detail"]


def test_revoke_all_affects_only_the_caller(two_users):
    (ana, ana_h), (bruno, bruno_h) = two_users

    assert ana.delete("/api/v1/users/me/sessions", headers=ana_h).status_code == 204

    assert ana.post("/api/v1/auth/refresh").status_code == 401
    assert bruno.post("/api/v1/auth/refresh").status_code == 200
    assert bruno.get("/api/v1/users/me/sessions", headers=bruno_h).json()


def test_revoking_own_session_blocks_its_refresh_token(two_users):
    (ana, ana_h), _ = two_users
    session_id = only_session_id(ana, ana_h)

    assert ana.delete(f"/api/v1/users/me/sessions/{session_id}", headers=ana_h).status_code == 204

    assert ana.post("/api/v1/auth/refresh").status_code == 401
    assert ana.get("/api/v1/users/me/sessions", headers=ana_h).json() == []


def test_rotated_session_is_listed_once(two_users):
    (ana, ana_h), _ = two_users
    ana.post("/api/v1/auth/refresh")
    ana.post("/api/v1/auth/refresh")
    assert len(ana.get("/api/v1/users/me/sessions", headers=ana_h).json()) == 1


def test_sessions_output_never_exposes_tokens(two_users):
    (ana, ana_h), _ = two_users
    body = ana.get("/api/v1/users/me/sessions", headers=ana_h).text
    assert "refresh_token" not in body
    assert "hash" not in body


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("GET", "/api/v1/users/me"),
        ("GET", "/api/v1/users/me/sessions"),
        ("DELETE", "/api/v1/users/me/sessions"),
        ("DELETE", f"/api/v1/users/me/sessions/{uuid.uuid4()}"),
    ],
)
def test_private_routes_require_authentication(client: TestClient, method: str, path: str):
    response = client.request(method, path)
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
