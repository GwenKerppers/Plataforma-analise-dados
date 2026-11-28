import uuid
from datetime import UTC, datetime, timedelta

import pytest
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import func, select
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.infrastructure import model_registry  # noqa: F401
from app.infrastructure.database import Base
from app.modules.authentication.models import UserSession
from app.modules.users.models import User


def make_user(email: str = "ana@exemplo.com") -> User:
    return User(email=email, password_hash="hash-de-teste", full_name="Ana")


def make_session(user_id: uuid.UUID, token_hash: str = "a" * 64) -> UserSession:
    return UserSession(
        user_id=user_id,
        family_id=uuid.uuid4(),
        refresh_token_hash=token_hash,
        expires_at=datetime.now(UTC) + timedelta(days=14),
    )


def test_migrations_match_models(engine: Engine):
    """A migração 0001 deve produzir exatamente o esquema declarado nos modelos."""
    with engine.connect() as connection:
        differences = compare_metadata(MigrationContext.configure(connection), Base.metadata)
    assert differences == []


def test_user_gets_defaults(db: Session):
    user = make_user()
    db.add(user)
    db.flush()
    db.refresh(user)
    assert isinstance(user.id, uuid.UUID)
    assert user.is_active is True
    assert user.created_at is not None


def test_email_is_unique(db: Session):
    db.add(make_user())
    db.flush()
    db.add(make_user())
    with pytest.raises(IntegrityError):
        db.flush()


def test_email_must_be_lowercase(db: Session):
    db.add(make_user("Ana@Exemplo.com"))
    with pytest.raises(IntegrityError):
        db.flush()


def test_sessions_are_deleted_with_user(db: Session):
    user = make_user()
    db.add(user)
    db.flush()
    db.add(make_session(user.id))
    db.flush()

    db.delete(user)
    db.flush()

    assert db.scalar(select(func.count()).select_from(UserSession)) == 0


def test_refresh_token_hash_is_unique(db: Session):
    user = make_user()
    db.add(user)
    db.flush()
    db.add(make_session(user.id, "b" * 64))
    db.flush()
    db.add(make_session(user.id, "b" * 64))
    with pytest.raises(IntegrityError):
        db.flush()


def test_revocation_fields_must_be_consistent(db: Session):
    user = make_user()
    db.add(user)
    db.flush()
    session = make_session(user.id)
    session.revoked_at = datetime.now(UTC)  # sem motivo
    db.add(session)
    with pytest.raises(IntegrityError):
        db.flush()


def test_revocation_reason_must_be_known(db: Session):
    user = make_user()
    db.add(user)
    db.flush()
    session = make_session(user.id)
    session.revoked_at = datetime.now(UTC)
    session.revoked_reason = "qualquer-coisa"
    db.add(session)
    with pytest.raises(IntegrityError):
        db.flush()
