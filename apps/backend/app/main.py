from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import health
from app.modules.authentication.api import router as auth_router
from app.modules.users.api import router as users_router
from app.core.config import get_settings
from app.core.errors import register_error_handlers
from app.core.logging import configure_logging
from app.core.middleware import RequestIdMiddleware

settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(title="Plataforma de Análise de Dados API", version="0.1.0")

register_error_handlers(app)
app.add_middleware(RequestIdMiddleware)
# CORS por último = camada mais externa.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,  # necessário para o cookie de refresh token (etapa 1.3)
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)

app.include_router(health.router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
