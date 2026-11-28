import logging
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.errors import ConflictError, UnauthorizedError
from app.modules.authentication.models import UserSession
from app.modules.authentication.repositories import SessionRepository
from app.modules.authentication.security import (
    burn_password_check,
    create_access_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from app.modules.users.models import User
from app.modules.users.repositories import UserRepository

logger = logging.getLogger("app.auth")


@dataclass(frozen=True)
class IssuedTokens:
    access_token: str
    refresh_token: str
    expires_in: int


def normalize_email(email: str) -> str:
    return email.strip().lower()


def _invalid_credentials() -> UnauthorizedError:
    return UnauthorizedError("Credenciais inválidas.")


def _invalid_session() -> UnauthorizedError:
    return UnauthorizedError("Sessão inválida ou expirada.")


class AuthService:
    def __init__(self, db: Session, settings: Settings) -> None:
        self.db = db
        self.settings = settings
        self.users = UserRepository(db)
        self.sessions = SessionRepository(db)

    def register(self, *, email: str, password: str, full_name: str) -> User:
        email = normalize_email(email)
        if self.users.get_by_email(email) is not None:
            raise ConflictError("E-mail já cadastrado.")

        user = User(email=email, password_hash=hash_password(password), full_name=full_name)
        self.users.add(user)
        try:
            self.db.commit()
        except IntegrityError as exc:  # cadastro simultâneo com o mesmo e-mail
            self.db.rollback()
            raise ConflictError("E-mail já cadastrado.") from exc
        self.db.refresh(user)
        return user

    def login(self, *, email: str, password: str, user_agent: str | None) -> IssuedTokens:
        user = self.users.get_by_email(normalize_email(email))
        if user is None:
            burn_password_check(password)
            raise _invalid_credentials()
        if not verify_password(user.password_hash, password) or not user.is_active:
            raise _invalid_credentials()
        return self._issue(user, family_id=uuid.uuid4(), user_agent=user_agent)

    def refresh(self, *, refresh_token: str, user_agent: str | None) -> IssuedTokens:
        now = datetime.now(UTC)
        session = self.sessions.get_by_token_hash(hash_refresh_token(refresh_token), lock=True)
        if session is None:
            raise _invalid_session()

        if session.revoked_at is not None:
            if session.revoked_reason == "rotated":
                # Token já usado apareceu de novo: possível roubo. Derruba a família inteira.
                self.sessions.revoke_family(session.family_id, "reuse_detected", now)
                self.db.commit()
                logger.warning(
                    "reuso de refresh token detectado",
                    extra={"context": {"user_id": str(session.user_id)}},
                )
            raise _invalid_session()

        if session.expires_at <= now:
            raise _invalid_session()

        user = self.users.get_by_id(session.user_id)
        if user is None or not user.is_active:
            raise _invalid_session()

        self.sessions.revoke(session, "rotated", now)
        return self._issue(user, family_id=session.family_id, user_agent=user_agent)

    def logout(self, *, refresh_token: str) -> None:
        """Encerra a sessão. Idempotente: token desconhecido não é erro."""
        session = self.sessions.get_by_token_hash(hash_refresh_token(refresh_token), lock=True)
        if session is not None:
            self.sessions.revoke_family(session.family_id, "logout", datetime.now(UTC))
            self.db.commit()

    def _issue(self, user: User, *, family_id: uuid.UUID, user_agent: str | None) -> IssuedTokens:
        raw_refresh = generate_refresh_token()
        self.sessions.add(
            UserSession(
                user_id=user.id,
                family_id=family_id,
                refresh_token_hash=hash_refresh_token(raw_refresh),
                user_agent=user_agent[:255] if user_agent else None,
                expires_at=datetime.now(UTC) + timedelta(days=self.settings.refresh_token_ttl_days),
            )
        )
        access = create_access_token(
            user.id,
            secret=self.settings.jwt_secret,
            ttl_minutes=self.settings.access_token_ttl_minutes,
        )
        self.db.commit()  # também persiste a revogação do token antigo, quando houver
        return IssuedTokens(
            access_token=access,
            refresh_token=raw_refresh,
            expires_in=self.settings.access_token_ttl_minutes * 60,
        )
