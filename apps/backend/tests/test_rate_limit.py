import time
import uuid
from collections.abc import Iterator

import pytest
import redis
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.core.rate_limit import RedisRateLimiter, get_rate_limiter
from app.main import app

PASSWORD = "senha-bem-longa-123"


@pytest.fixture
def redis_client() -> Iterator[redis.Redis]:
    client = redis.Redis.from_url(get_settings().redis_url)
    yield client
    client.close()


def new_limiter(client: redis.Redis) -> RedisRateLimiter:
    # Prefixo único por teste: nenhum teste enxerga a contagem de outro.
    return RedisRateLimiter(client, prefix=f"test:{uuid.uuid4().hex}")


# ---------- limitador (Redis real) ----------


def test_blocks_after_limit_with_retry_after(redis_client: redis.Redis):
    limiter = new_limiter(redis_client)
    results = [limiter.hit("k", limit=3, window_seconds=60) for _ in range(5)]
    assert [r.allowed for r in results] == [True, True, True, False, False]
    assert 1 <= results[3].retry_after <= 60


def test_keys_are_independent(redis_client: redis.Redis):
    limiter = new_limiter(redis_client)
    assert limiter.hit("a", limit=1, window_seconds=60).allowed
    assert not limiter.hit("a", limit=1, window_seconds=60).allowed
    assert limiter.hit("b", limit=1, window_seconds=60).allowed


def test_window_resets(redis_client: redis.Redis):
    limiter = new_limiter(redis_client)
    assert limiter.hit("k", limit=1, window_seconds=1).allowed
    assert not limiter.hit("k", limit=1, window_seconds=1).allowed
    time.sleep(1.2)
    assert limiter.hit("k", limit=1, window_seconds=1).allowed


def test_fails_open_when_redis_is_down():
    dead = redis.Redis(host="127.0.0.1", port=1, socket_connect_timeout=0.2)
    assert RedisRateLimiter(dead).hit("k", limit=1, window_seconds=60).allowed


# ---------- endpoints ----------


@pytest.fixture
def limited_client(client: TestClient, redis_client: redis.Redis) -> TestClient:
    """O `client` comum, mas com limitador real e limites baixos. O teardown de `client`
    limpa todos os overrides."""
    limiter = new_limiter(redis_client)
    settings = get_settings().model_copy(
        update={
            "rate_limit_register_per_hour": 2,
            "rate_limit_login_per_ip_per_minute": 5,
            "rate_limit_login_per_email_per_minute": 2,
            "rate_limit_refresh_per_minute": 2,
        }
    )
    app.dependency_overrides[get_rate_limiter] = lambda: limiter
    app.dependency_overrides[get_settings] = lambda: settings
    return client


def register(client: TestClient, email: str):
    return client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": PASSWORD, "full_name": "Ana"},
    )


def login(client: TestClient, email: str, password: str = PASSWORD):
    return client.post("/api/v1/auth/login", json={"email": email, "password": password})


def test_register_is_rate_limited(limited_client: TestClient):
    assert register(limited_client, "a1@exemplo.com").status_code == 201
    assert register(limited_client, "a2@exemplo.com").status_code == 201

    response = register(limited_client, "a3@exemplo.com")
    assert response.status_code == 429
    assert response.json()["code"] == "rate_limited"
    assert response.headers["content-type"].startswith("application/problem+json")
    assert int(response.headers["retry-after"]) >= 1


def test_login_is_limited_per_email_even_with_correct_password(limited_client: TestClient):
    register(limited_client, "ana@exemplo.com")
    assert login(limited_client, "ana@exemplo.com", "errada-errada-123").status_code == 401
    assert login(limited_client, "ana@exemplo.com", "errada-errada-456").status_code == 401

    blocked = login(limited_client, "ana@exemplo.com")  # senha correta, mas já no limite
    assert blocked.status_code == 429
    assert int(blocked.headers["retry-after"]) >= 1

    # Outro e-mail não é afetado pelo limite do primeiro.
    assert login(limited_client, "outra@exemplo.com").status_code == 401


def test_login_is_limited_per_ip_across_emails(limited_client: TestClient):
    statuses = [login(limited_client, f"u{i}@exemplo.com").status_code for i in range(6)]
    assert statuses == [401, 401, 401, 401, 401, 429]


def test_refresh_is_rate_limited(limited_client: TestClient):
    statuses = [limited_client.post("/api/v1/auth/refresh").status_code for _ in range(3)]
    assert statuses == [401, 401, 429]
