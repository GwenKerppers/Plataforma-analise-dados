"""Funções puras de segurança: senhas, access token (JWT) e refresh token."""

import hashlib
import secrets
import uuid
from datetime import UTC, datetime, timedelta
from functools import lru_cache

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

from app.core.errors import UnauthorizedError

ALGORITHM = "HS256"

_hasher = PasswordHasher()  # Argon2id com os parâmetros padrão recomendados


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    try:
        return _hasher.verify(password_hash, password)
    except (VerificationError, InvalidHashError):
        return False


@lru_cache
def _dummy_hash() -> str:
    return _hasher.hash("senha-ficticia-para-igualar-o-tempo-de-resposta")


def burn_password_check(password: str) -> None:
    """Gasta o mesmo tempo de uma verificação real quando o usuário não existe.

    Evita que a diferença de tempo revele se um e-mail está cadastrado.
    """
    verify_password(_dummy_hash(), password)


def create_access_token(
    user_id: uuid.UUID, *, secret: str, ttl_minutes: int, now: datetime | None = None
) -> str:
    issued_at = now or datetime.now(UTC)
    payload = {
        "sub": str(user_id),
        "typ": "access",
        "iat": issued_at,
        "exp": issued_at + timedelta(minutes=ttl_minutes),
    }
    return jwt.encode(payload, secret, algorithm=ALGORITHM)


def decode_access_token(token: str, *, secret: str) -> uuid.UUID:
    try:
        payload = jwt.decode(
            token, secret, algorithms=[ALGORITHM], options={"require": ["exp", "sub"]}
        )
        if payload.get("typ") != "access":
            raise jwt.InvalidTokenError("tipo de token inválido")
        return uuid.UUID(payload["sub"])
    except (jwt.PyJWTError, ValueError, KeyError) as exc:
        raise UnauthorizedError("Token inválido ou expirado.") from exc


def generate_refresh_token() -> str:
    return secrets.token_urlsafe(48)


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()
