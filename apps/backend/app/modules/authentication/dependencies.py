from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.errors import UnauthorizedError
from app.core.rate_limit import RateLimiter, get_rate_limiter
from app.infrastructure.database import get_db
from app.modules.authentication.security import decode_access_token
from app.modules.authentication.services import AuthService
from app.modules.users.models import User
from app.modules.users.repositories import UserRepository

bearer_scheme = HTTPBearer(auto_error=False)

DbDep = Annotated[Session, Depends(get_db)]
SettingsDep = Annotated[Settings, Depends(get_settings)]
RateLimiterDep = Annotated[RateLimiter, Depends(get_rate_limiter)]


def get_auth_service(db: DbDep, settings: SettingsDep) -> AuthService:
    return AuthService(db, settings)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: DbDep,
    settings: SettingsDep,
) -> User:
    """Identifica o usuário a partir do access token. A autorização é sempre feita aqui,
    no backend, e nunca depende de verificações do frontend."""
    if credentials is None:
        raise UnauthorizedError("Autenticação necessária.")
    user_id = decode_access_token(credentials.credentials, secret=settings.jwt_secret)
    user = UserRepository(db).get_by_id(user_id)
    if user is None or not user.is_active:
        raise UnauthorizedError("Token inválido ou expirado.")
    return user


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
CurrentUser = Annotated[User, Depends(get_current_user)]
