import hashlib
import uuid
from typing import Annotated

from fastapi import APIRouter, Cookie, Request, Response

from app.core.config import Settings
from app.core.errors import UnauthorizedError
from app.core.rate_limit import enforce_rate_limit
from app.modules.authentication.dependencies import (
    AuthServiceDep,
    CurrentUser,
    RateLimiterDep,
    SettingsDep,
)
from app.modules.authentication.schemas import LoginIn, RegisterIn, SessionOut, TokenOut
from app.modules.authentication.services import IssuedTokens, normalize_email
from app.modules.users.schemas import UserOut

router = APIRouter(prefix="/auth", tags=["auth"])
sessions_router = APIRouter(prefix="/users/me/sessions", tags=["sessions"])

REFRESH_COOKIE = "refresh_token"
# O cookie só é enviado às rotas de autenticação, nunca a outras rotas da API.
REFRESH_COOKIE_PATH = "/api/v1/auth"


def _user_agent(request: Request) -> str | None:
    return request.headers.get("user-agent")


def _client_ip(request: Request) -> str:
    # Atrás de um proxy, configure o uvicorn para confiar nos cabeçalhos dele (ADR-010).
    return request.client.host if request.client else "unknown"


def _email_key(email: str) -> str:
    """Chave do limite por e-mail: hash, para não gravar e-mails no Redis."""
    return hashlib.sha256(normalize_email(email).encode()).hexdigest()[:32]


def _set_refresh_cookie(response: Response, token: str, settings: Settings) -> None:
    response.set_cookie(
        REFRESH_COOKIE,
        token,
        max_age=settings.refresh_token_ttl_days * 24 * 60 * 60,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="strict",
        path=REFRESH_COOKIE_PATH,
    )


def _token_response(issued: IssuedTokens, response: Response, settings: Settings) -> TokenOut:
    _set_refresh_cookie(response, issued.refresh_token, settings)
    return TokenOut(access_token=issued.access_token, expires_in=issued.expires_in)


@router.post("/register", response_model=UserOut, status_code=201)
def register(
    body: RegisterIn,
    request: Request,
    service: AuthServiceDep,
    limiter: RateLimiterDep,
    settings: SettingsDep,
) -> UserOut:
    enforce_rate_limit(
        limiter,
        f"register:ip:{_client_ip(request)}",
        limit=settings.rate_limit_register_per_hour,
        window_seconds=3600,
    )
    user = service.register(email=body.email, password=body.password, full_name=body.full_name)
    return UserOut.model_validate(user)


@router.post("/login", response_model=TokenOut)
def login(
    body: LoginIn,
    request: Request,
    response: Response,
    service: AuthServiceDep,
    limiter: RateLimiterDep,
    settings: SettingsDep,
) -> TokenOut:
    enforce_rate_limit(
        limiter,
        f"login:ip:{_client_ip(request)}",
        limit=settings.rate_limit_login_per_ip_per_minute,
        window_seconds=60,
    )
    enforce_rate_limit(
        limiter,
        f"login:email:{_email_key(body.email)}",
        limit=settings.rate_limit_login_per_email_per_minute,
        window_seconds=60,
    )
    issued = service.login(
        email=body.email, password=body.password, user_agent=_user_agent(request)
    )
    return _token_response(issued, response, settings)


@router.post("/refresh", response_model=TokenOut)
def refresh(
    request: Request,
    response: Response,
    service: AuthServiceDep,
    limiter: RateLimiterDep,
    settings: SettingsDep,
    refresh_token: Annotated[str | None, Cookie()] = None,
) -> TokenOut:
    enforce_rate_limit(
        limiter,
        f"refresh:ip:{_client_ip(request)}",
        limit=settings.rate_limit_refresh_per_minute,
        window_seconds=60,
    )
    if not refresh_token:
        raise UnauthorizedError("Sessão ausente.")
    issued = service.refresh(refresh_token=refresh_token, user_agent=_user_agent(request))
    return _token_response(issued, response, settings)


@router.post("/logout", status_code=204)
def logout(
    service: AuthServiceDep,
    refresh_token: Annotated[str | None, Cookie()] = None,
) -> Response:
    if refresh_token:
        service.logout(refresh_token=refresh_token)
    response = Response(status_code=204)
    response.delete_cookie(REFRESH_COOKIE, path=REFRESH_COOKIE_PATH)
    return response


@sessions_router.get("", response_model=list[SessionOut])
def list_sessions(user: CurrentUser, service: AuthServiceDep) -> list[SessionOut]:
    return [
        SessionOut(
            id=row.family_id,
            user_agent=row.user_agent,
            last_active_at=row.created_at,
            expires_at=row.expires_at,
        )
        for row in service.list_sessions(user)
    ]


@sessions_router.delete("/{session_id}", status_code=204)
def revoke_session(session_id: uuid.UUID, user: CurrentUser, service: AuthServiceDep) -> Response:
    service.revoke_session(user, session_id)
    return Response(status_code=204)


@sessions_router.delete("", status_code=204)
def revoke_all_sessions(user: CurrentUser, service: AuthServiceDep) -> Response:
    service.revoke_all_sessions(user)
    return Response(status_code=204)
