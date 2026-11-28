"""Fixtures de banco.

Os testes usam um banco separado (`<nome>_test`), recriado a cada execução e migrado com o
Alembic, o que também valida as migrações. Exigem PostgreSQL acessível via DATABASE_URL
(no Docker Compose: `docker compose run --rm backend pytest`).
"""

import os

# Segredo de teste, definido ANTES de qualquer import da aplicação (o Settings o exige).
os.environ.setdefault("JWT_SECRET", "segredo-apenas-para-testes-0123456789abcdef")

from collections.abc import Iterator  # noqa: E402
from pathlib import Path  # noqa: E402

import pytest  # noqa: E402
from alembic import command  # noqa: E402
from alembic.config import Config  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine, text  # noqa: E402
from sqlalchemy.engine import Engine, make_url  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from app.core.config import get_settings  # noqa: E402
from app.infrastructure.database import get_db  # noqa: E402
from app.main import app  # noqa: E402

BACKEND_DIR = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def test_database_url() -> str:
    base = make_url(get_settings().database_url)
    test_name = f"{base.database}_test"

    admin = create_engine(base.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with admin.connect() as connection:
        connection.execute(text(f'DROP DATABASE IF EXISTS "{test_name}" WITH (FORCE)'))
        connection.execute(text(f'CREATE DATABASE "{test_name}"'))
    admin.dispose()

    url = base.set(database=test_name).render_as_string(hide_password=False)

    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    config.set_main_option("sqlalchemy.url", url.replace("%", "%%"))
    command.upgrade(config, "head")
    return url


@pytest.fixture(scope="session")
def engine(test_database_url: str) -> Iterator[Engine]:
    test_engine = create_engine(test_database_url)
    yield test_engine
    test_engine.dispose()


@pytest.fixture
def db(engine: Engine) -> Iterator[Session]:
    """Sessão isolada: tudo que o teste gravar é desfeito ao final."""
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def client(db: Session) -> Iterator[TestClient]:
    """Cliente HTTP cujas requisições usam a sessão de teste (tudo é desfeito ao final)."""
    app.dependency_overrides[get_db] = lambda: db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
