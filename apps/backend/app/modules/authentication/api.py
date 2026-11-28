from typing import Annotated

from fastapi import APIRouter, Cookie, Request, Response

from app.core.errors import UnauthorizedError
from app.core.config import Settings
from app.modules.authentication.dependencies import AuthServiceDep, SettingsDep
from app.modules.authentication.schemas import LoginIn, RegisterIn, TokenOut
from app.modules.authentication.services import IssuedTokens
from app.modules.users.schemas import UserOut

router = APIRouter(prefix="/auth", tags=["auth"])

REFRESH_COOKIE = "refresh_token"
# O cookie só é enviado às rotas de autenticação, nunca a outras rotas da API.
REFRESH_COOKIE_PATH = "/api/v1/auth"


def _user_agent(request: Request) -> str | None:
    return request.headers.get("user-agent")


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
def register(body: RegisterIn, service: AuthServiceDep) -> UserOut:
    user = service.register(email=body.email, password=body.password, full_name=body.full_name)
    return UserOut.model_validate(user)


@router.post("/login", response_model=TokenOut)
def login(
    body: LoginIn,
    request: Request,
    response: Response,
    service: AuthServiceDep,
    settings: SettingsDep,
) -> TokenOut:
    issued = service.login(
        email=body.email, password=body.password, user_agent=_user_agent(request)
    )
    return _token_response(issued, response, settings)


@router.post("/refresh", response_model=TokenOut)
def refresh(
    request: Request,
    response: Response,
    service: AuthServiceDep,
    settings: SettingsDep,
    refresh_token: Annotated[str | None, Cookie()] = None,
) -> TokenOut:
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
