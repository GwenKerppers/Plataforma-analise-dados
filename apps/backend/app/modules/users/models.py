import uuid

from sqlalchemy import CheckConstraint, String, true
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database import Base, TimestampMixin


class User(TimestampMixin, Base):
    __tablename__ = "users"
    __table_args__ = (
        # O e-mail é sempre normalizado em minúsculas pelo serviço; o banco garante.
        CheckConstraint("email = lower(email)", name="email_lowercase"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(320), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(120))
    is_active: Mapped[bool] = mapped_column(default=True, server_default=true())
