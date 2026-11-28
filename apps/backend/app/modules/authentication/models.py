import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database import Base


class UserSession(Base):
    """Um refresh token emitido. Cada rotação cria uma nova linha na mesma `family_id`.

    Reapresentar um token já rotacionado indica roubo: a família inteira é revogada.
    Guardamos apenas o hash (SHA-256 hex) do token, nunca o token.
    """

    __tablename__ = "user_sessions"
    __table_args__ = (
        CheckConstraint(
            "revoked_reason IS NULL OR revoked_reason IN ('rotated', 'logout', 'reuse_detected')",
            name="revoked_reason_valid",
        ),
        CheckConstraint(
            "(revoked_at IS NULL) = (revoked_reason IS NULL)",
            name="revocation_consistent",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    family_id: Mapped[uuid.UUID] = mapped_column(index=True)
    refresh_token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    user_agent: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    revoked_reason: Mapped[str | None] = mapped_column(String(32))
