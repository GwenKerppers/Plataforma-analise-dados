"""Limitação de requisições por janela fixa, contada no Redis."""

import logging
from dataclasses import dataclass
from functools import lru_cache
from typing import Protocol

import redis

from app.core.config import get_settings
from app.core.errors import TooManyRequestsError

logger = logging.getLogger("app.rate_limit")


@dataclass(frozen=True)
class RateLimitResult:
    allowed: bool
    retry_after: int = 0  # segundos até a janela reiniciar (só relevante se bloqueado)


class RateLimiter(Protocol):
    def hit(self, key: str, *, limit: int, window_seconds: int) -> RateLimitResult: ...


class NullRateLimiter:
    """Sem limite. Usado em testes que não exercitam a limitação."""

    def hit(self, key: str, *, limit: int, window_seconds: int) -> RateLimitResult:
        return RateLimitResult(allowed=True)


class RedisRateLimiter:
    """Janela fixa que começa na primeira requisição da chave.

    Se o Redis estiver indisponível, **libera** a requisição e registra erro (fail open):
    preferimos manter o login funcionando a derrubá-lo; o alerta fica no log.
    """

    def __init__(self, client: redis.Redis, prefix: str = "rl") -> None:
        self.client = client
        self.prefix = prefix

    def hit(self, key: str, *, limit: int, window_seconds: int) -> RateLimitResult:
        full_key = f"{self.prefix}:{key}"
        try:
            pipe = self.client.pipeline(transaction=True)
            pipe.incr(full_key)
            pipe.expire(full_key, window_seconds, nx=True)  # só define o TTL na 1ª requisição
            pipe.ttl(full_key)
            count, _, ttl = pipe.execute()
        except redis.RedisError:
            logger.error("redis indisponível; rate limit ignorado", exc_info=True)
            return RateLimitResult(allowed=True)

        if count <= limit:
            return RateLimitResult(allowed=True)
        return RateLimitResult(allowed=False, retry_after=max(int(ttl), 1))


def enforce_rate_limit(
    limiter: RateLimiter, key: str, *, limit: int, window_seconds: int
) -> None:
    result = limiter.hit(key, limit=limit, window_seconds=window_seconds)
    if not result.allowed:
        raise TooManyRequestsError(result.retry_after)


@lru_cache
def _redis_client() -> redis.Redis:
    return redis.Redis.from_url(
        get_settings().redis_url, socket_connect_timeout=1, socket_timeout=1
    )


def get_rate_limiter() -> RateLimiter:
    return RedisRateLimiter(_redis_client())
