"""Importa todos os modelos para que o SQLAlchemy/Alembic os conheçam.

Ao criar um novo módulo com tabelas, adicione o import aqui.
"""

from app.modules.authentication.models import UserSession  # noqa: F401
from app.modules.users.models import User  # noqa: F401
