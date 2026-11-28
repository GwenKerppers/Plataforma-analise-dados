import uuid
from datetime import UTC, datetime, timedelta

import jwt
import pytest

from app.core.errors import UnauthorizedError
from app.modules.authentication.security import (
    create_access_token,
    decode_access_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)

SECRET = "segredo-apenas-para-testes-0123456789abcdef"


def test_password_hash_is_argon2id_and_verifies():
    password_hash = hash_password("uma-senha-bem-longa")
    assert password_hash.startswith("$argon2id$")
    assert verify_password(password_hash, "uma-senha-bem-longa") is True
    assert verify_password(password_hash, "outra-senha-qualquer") is False


def test_verify_password_with_garbage_hash_is_false():
    assert verify_password("isto-nao-e-um-hash", "qualquer") is False


def test_access_token_roundtrip():
    user_id = uuid.uuid4()
    token = create_access_token(user_id, secret=SECRET, ttl_minutes=15)
    assert decode_access_token(token, secret=SECRET) == user_id


def test_access_token_rejects_wrong_secret():
    token = create_access_token(uuid.uuid4(), secret=SECRET, ttl_minutes=15)
    with pytest.raises(UnauthorizedError):
        decode_access_token(token, secret="outro-segredo-totalmente-diferente-123456")


def test_access_token_rejects_expired():
    past = datetime.now(UTC) - timedelta(hours=1)
    token = create_access_token(uuid.uuid4(), secret=SECRET, ttl_minutes=15, now=past)
    with pytest.raises(UnauthorizedError):
        decode_access_token(token, secret=SECRET)


def test_access_token_rejects_tampering():
    token = create_access_token(uuid.uuid4(), secret=SECRET, ttl_minutes=15)
    header, payload, signature = token.split(".")
    with pytest.raises(UnauthorizedError):
        decode_access_token(f"{header}.{payload}.{signature[::-1]}", secret=SECRET)


def test_access_token_rejects_wrong_type_and_alg_none():
    now = datetime.now(UTC)
    claims = {"sub": str(uuid.uuid4()), "typ": "refresh", "exp": now + timedelta(minutes=5)}
    with pytest.raises(UnauthorizedError):
        decode_access_token(jwt.encode(claims, SECRET, algorithm="HS256"), secret=SECRET)

    unsigned = jwt.encode({**claims, "typ": "access"}, key=None, algorithm="none")
    with pytest.raises(UnauthorizedError):
        decode_access_token(unsigned, secret=SECRET)


def test_refresh_token_is_random_and_hash_is_stable():
    first, second = generate_refresh_token(), generate_refresh_token()
    assert first != second
    assert len(first) >= 48
    assert hash_refresh_token(first) == hash_refresh_token(first)
    assert len(hash_refresh_token(first)) == 64
    assert hash_refresh_token(first) != first
