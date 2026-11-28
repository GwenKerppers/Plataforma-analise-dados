from functools import lru_cache

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "development"
    log_level: str = "INFO"
    database_url: str = "postgresql+psycopg://analise:analise@db:5432/analise"
    redis_url: str = "redis://redis:6379/0"
    # Origens do frontend autorizadas a chamar a API (CORS). Em produção, definir explicitamente.
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # Obrigatório (sem valor padrão): a aplicação não sobe sem segredo (fail fast).
    jwt_secret: str = Field(min_length=32)
    access_token_ttl_minutes: int = Field(default=15, ge=1)
    refresh_token_ttl_days: int = Field(default=14, ge=1)

    # Limites de requisições (janela fixa, contada no Redis). Ver ADR-010.
    rate_limit_register_per_hour: int = Field(default=10, ge=1)
    rate_limit_login_per_ip_per_minute: int = Field(default=20, ge=1)
    rate_limit_login_per_email_per_minute: int = Field(default=5, ge=1)
    rate_limit_refresh_per_minute: int = Field(default=60, ge=1)

    @model_validator(mode="after")
    def _reject_placeholder_secret(self) -> "Settings":
        if self.environment != "development" and self.jwt_secret.startswith("change-me"):
            raise ValueError("JWT_SECRET ainda é o valor de exemplo; gere um segredo aleatório.")
        return self

    @property
    def cookie_secure(self) -> bool:
        """Cookies só por HTTPS fora do ambiente de desenvolvimento."""
        return self.environment != "development"


@lru_cache
def get_settings() -> Settings:
    return Settings()
