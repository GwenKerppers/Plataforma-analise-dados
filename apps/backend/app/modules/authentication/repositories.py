import uuid
from datetime import datetime

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.modules.authentication.models import UserSession


class SessionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def add(self, session: UserSession) -> None:
        self.db.add(session)

    def get_by_token_hash(self, token_hash: str, *, lock: bool = False) -> UserSession | None:
        statement = select(UserSession).where(UserSession.refresh_token_hash == token_hash)
        if lock:
            # Serializa renovações concorrentes do mesmo token.
            statement = statement.with_for_update()
        return self.db.scalar(statement)

    def revoke(self, session: UserSession, reason: str, now: datetime) -> None:
        session.revoked_at = now
        session.revoked_reason = reason

    def revoke_family(self, family_id: uuid.UUID, reason: str, now: datetime) -> None:
        """Revoga todos os tokens ainda ativos da família (já revogados ficam como estão)."""
        self.db.execute(
            update(UserSession)
            .where(UserSession.family_id == family_id, UserSession.revoked_at.is_(None))
            .values(revoked_at=now, revoked_reason=reason)
        )

    def list_active_for_user(self, user_id: uuid.UUID, now: datetime) -> list[UserSession]:
        """Sessões ativas: o token não revogado e não expirado de cada família."""
        statement = (
            select(UserSession)
            .where(
                UserSession.user_id == user_id,
                UserSession.revoked_at.is_(None),
                UserSession.expires_at > now,
            )
            .order_by(UserSession.created_at.desc())
        )
        return list(self.db.scalars(statement))

    def has_active_family(self, user_id: uuid.UUID, family_id: uuid.UUID, now: datetime) -> bool:
        """Só considera sessões do próprio usuário: família alheia equivale a inexistente."""
        count = self.db.scalar(
            select(func.count())
            .select_from(UserSession)
            .where(
                UserSession.user_id == user_id,
                UserSession.family_id == family_id,
                UserSession.revoked_at.is_(None),
                UserSession.expires_at > now,
            )
        )
        return bool(count)

    def revoke_all_for_user(self, user_id: uuid.UUID, reason: str, now: datetime) -> None:
        self.db.execute(
            update(UserSession)
            .where(UserSession.user_id == user_id, UserSession.revoked_at.is_(None))
            .values(revoked_at=now, revoked_reason=reason)
        )
