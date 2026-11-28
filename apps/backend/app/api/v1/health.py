import logging
from typing import Annotated

import redis
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.infrastructure.database import get_db

logger = logging.getLogger("app.health")

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    """Liveness: o processo está de pé."""
    return {"status": "ok"}


@router.get("/health/ready")
def ready(db: Annotated[Session, Depends(get_db)]) -> JSONResponse:
    """Readiness: dependências essenciais respondem. Retorna 503 se alguma falhar."""
    checks: dict[str, str] = {}

    try:
        db.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception:
        logger.exception("falha na checagem do banco")
        checks["database"] = "error"

    try:
        client = redis.Redis.from_url(get_settings().redis_url, socket_connect_timeout=2)
        client.ping()
        checks["redis"] = "ok"
    except Exception:
        logger.exception("falha na checagem do redis")
        checks["redis"] = "error"

    healthy = all(value == "ok" for value in checks.values())
    return JSONResponse(
        {"status": "ok" if healthy else "degraded", "checks": checks},
        status_code=200 if healthy else 503,
    )
