from alembic import context
from sqlalchemy import create_engine, pool

from app.core.config import get_settings
from app.infrastructure import model_registry  # noqa: F401  (registra os modelos no metadata)
from app.infrastructure.database import Base

config = context.config
target_metadata = Base.metadata


def get_url() -> str:
    # Os testes sobrescrevem a URL via config; no uso normal vale a configuração da aplicação.
    return config.get_main_option("sqlalchemy.url") or get_settings().database_url


def run_migrations_offline() -> None:
    context.configure(
        url=get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    engine = create_engine(get_url(), poolclass=pool.NullPool)
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
