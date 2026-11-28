from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.modules.authentication.models import UserSession
from app.modules.authentication.security import create_access_token
from app.modules.users.models import User

EMAIL = "ana@exemplo.com"
PASSWORD = "senha-bem-longa-123"
SECRET = "segredo-apenas-para-testes-0123456789abcdef"


def register(client: TestClient, email: str = EMAIL, password: str = PASSWORD):
    return client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": "Ana Souza"},
    )


def login(client: TestClient, email: str = EMAIL, password: str = PASSWORD):
    return client.post("/api/v1/auth/login", json={"email": email, "password": password})


def refresh_with(client: TestClient, token: str):
    # Cabeçalho explícito: simula um cliente (ou atacante) que apresenta um token específico.
    return client.post("/api/v1/auth/refresh", headers={"Cookie": f"refresh_token={token}"})


def auth_header(access_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}"}


# ---------- cadastro ----------


def test_register_creates_user_without_exposing_hash(client: TestClient, db: Session):
    response = register(client, "ANA@Exemplo.com")
    body = response.json()

    assert response.status_code == 201
    assert body["email"] == EMAIL  # normalizado
    assert "password" not in body and "password_hash" not in body

    user = db.scalar(select(User).where(User.email == EMAIL))
    assert user is not None
    assert user.password_hash.startswith("$argon2id$")
    assert PASSWORD not in user.password_hash


def test_register_duplicate_email_conflicts_case_insensitive(client: TestClient):
    assert register(client).status_code == 201
    response = register(client, "ANA@EXEMPLO.COM")
    assert response.status_code == 409
    assert response.json()["code"] == "conflict"


def test_register_rejects_short_password_and_bad_email(client: TestClient):
    assert register(client, password="curta").status_code == 422
    assert register(client, email="nao-e-email").status_code == 422


# ---------- login ----------


def test_login_returns_access_token_and_secure_refresh_cookie(client: TestClient, db: Session):
    register(client)
    response = login(client)
    body = response.json()
    assert response.status_code == 200
    assert body["token_type"] == "bearer"
    assert body["expires_in"] == 15 * 60

    cookie = response.headers["set-cookie"].lower()
    assert "httponly" in cookie
    assert "samesite=strict" in cookie
    assert "path=/api/v1/auth" in cookie

    raw_token = client.cookies.get("refresh_token")
    stored = db.scalars(select(UserSession)).all()
    assert len(stored) == 1
    assert stored[0].refresh_token_hash != raw_token  # só o hash é guardado


def test_login_failures_are_indistinguishable(client: TestClient):
    register(client)
    wrong_password = login(client, password="senha-errada-123456")
    unknown_user = login(client, email="ninguem@exemplo.com")
    assert wrong_password.status_code == unknown_user.status_code == 401
    assert wrong_password.json()["detail"] == unknown_user.json()["detail"]


def test_inactive_user_cannot_login(client: TestClient, db: Session):
    register(client)
    db.execute(update(User).values(is_active=False))
    db.expire_all()
    assert login(client).status_code == 401


# ---------- /users/me ----------


def test_me_with_valid_token(client: TestClient):
    register(client)
    token = login(client).json()["access_token"]
    response = client.get("/api/v1/users/me", headers=auth_header(token))
    assert response.status_code == 200
    assert response.json()["email"] == EMAIL


def test_me_requires_authentication(client: TestClient):
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.headers["www-authenticate"] == "Bearer"


def test_me_rejects_garbage_and_expired_tokens(client: TestClient, db: Session):
    register(client)
    assert client.get("/api/v1/users/me", headers=auth_header("lixo")).status_code == 401

    user = db.scalar(select(User))
    expired = create_access_token(
        user.id, secret=SECRET, ttl_minutes=15, now=datetime.now(UTC) - timedelta(hours=1)
    )
    assert client.get("/api/v1/users/me", headers=auth_header(expired)).status_code == 401


def test_me_rejects_token_of_deleted_user(client: TestClient, db: Session):
    register(client)
    token = login(client).json()["access_token"]
    db.delete(db.scalar(select(User)))
    db.flush()
    assert client.get("/api/v1/users/me", headers=auth_header(token)).status_code == 401


# ---------- refresh ----------


def test_refresh_rotates_token(client: TestClient, db: Session):
    register(client)
    login(client)
    old = client.cookies.get("refresh_token")

    response = client.post("/api/v1/auth/refresh")
    assert response.status_code == 200
    assert response.json()["access_token"]
    assert client.cookies.get("refresh_token") != old

    rows = db.scalars(select(UserSession)).all()
    assert len(rows) == 2
    assert len({row.family_id for row in rows}) == 1
    assert sorted(row.revoked_reason or "" for row in rows) == ["", "rotated"]


def test_reusing_rotated_token_revokes_whole_family(client: TestClient, db: Session):
    register(client)
    login(client)
    old = client.cookies.get("refresh_token")
    assert client.post("/api/v1/auth/refresh").status_code == 200
    current = client.cookies.get("refresh_token")

    assert refresh_with(client, old).status_code == 401  # reuso detectado
    assert refresh_with(client, current).status_code == 401  # família derrubada

    reasons = set(db.scalars(select(UserSession.revoked_reason)))
    assert reasons == {"rotated", "reuse_detected"}


def test_refresh_without_cookie_or_with_unknown_token(client: TestClient):
    assert client.post("/api/v1/auth/refresh").status_code == 401
    assert refresh_with(client, "token-desconhecido").status_code == 401


def test_refresh_rejects_expired_session(client: TestClient, db: Session):
    register(client)
    login(client)
    db.execute(update(UserSession).values(expires_at=datetime.now(UTC) - timedelta(seconds=1)))
    db.expire_all()
    assert client.post("/api/v1/auth/refresh").status_code == 401


# ---------- logout ----------


def test_logout_revokes_session(client: TestClient, db: Session):
    register(client)
    login(client)
    token = client.cookies.get("refresh_token")

    assert client.post("/api/v1/auth/logout").status_code == 204
    assert refresh_with(client, token).status_code == 401
    assert set(db.scalars(select(UserSession.revoked_reason))) == {"logout"}


def test_logout_is_idempotent_without_session(client: TestClient):
    assert client.post("/api/v1/auth/logout").status_code == 204
