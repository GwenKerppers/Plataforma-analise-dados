"""Erros de domínio e respostas no formato Problem Details (RFC 9457)."""

import logging
from http import HTTPStatus

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.requests import Request

logger = logging.getLogger("app.errors")

PROBLEM_JSON = "application/problem+json"


class AppError(Exception):
    """Base dos erros esperados da aplicação. Subclasses definem status e código estável."""

    status_code = 500
    code = "internal_error"
    title = "Erro interno"
    headers: dict[str, str] | None = None

    def __init__(self, detail: str | None = None) -> None:
        super().__init__(detail or self.title)
        self.detail = detail or self.title


class NotFoundError(AppError):
    status_code = 404
    code = "not_found"
    title = "Recurso não encontrado"


class UnauthorizedError(AppError):
    status_code = 401
    code = "unauthorized"
    title = "Não autenticado"
    headers = {"WWW-Authenticate": "Bearer"}


class ConflictError(AppError):
    status_code = 409
    code = "conflict"
    title = "Conflito"


def _problem(
    request: Request,
    *,
    status: int,
    title: str,
    detail: str,
    code: str,
    headers: dict[str, str] | None = None,
    extra: dict[str, object] | None = None,
) -> JSONResponse:
    body: dict[str, object] = {
        "type": "about:blank",
        "title": title,
        "status": status,
        "detail": detail,
        "instance": request.url.path,
        "code": code,
        "request_id": getattr(request.state, "request_id", None),
    }
    if extra:
        body.update(extra)
    return JSONResponse(body, status_code=status, media_type=PROBLEM_JSON, headers=headers)


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
        return _problem(
            request,
            status=exc.status_code,
            title=exc.title,
            detail=exc.detail,
            code=exc.code,
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation(request: Request, exc: RequestValidationError) -> JSONResponse:
        # Não devolvemos o valor enviado (`input`), para não ecoar dados sensíveis.
        errors = [
            {"loc": list(e["loc"]), "msg": e["msg"], "type": e["type"]} for e in exc.errors()
        ]
        return _problem(
            request,
            status=422,
            title="Dados inválidos",
            detail="Um ou mais campos são inválidos.",
            code="validation_error",
            extra={"errors": errors},
        )

    @app.exception_handler(StarletteHTTPException)
    async def handle_http(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        phrase = HTTPStatus(exc.status_code).phrase
        detail = exc.detail if isinstance(exc.detail, str) else phrase
        return _problem(
            request,
            status=exc.status_code,
            title=phrase,
            detail=detail,
            code=f"http_{exc.status_code}",
            headers=dict(exc.headers) if exc.headers else None,
        )

    @app.exception_handler(Exception)
    async def handle_unexpected(request: Request, exc: Exception) -> JSONResponse:
        # Detalhes e stack trace ficam só no log do servidor, nunca na resposta.
        logger.exception("erro inesperado")
        return _problem(
            request,
            status=500,
            title="Erro interno",
            detail="Ocorreu um erro inesperado. Informe o request_id ao suporte.",
            code="internal_error",
        )
