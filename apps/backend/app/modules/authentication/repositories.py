import uuid
from datetime import datetime

from sqlalchemy import select, update
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
