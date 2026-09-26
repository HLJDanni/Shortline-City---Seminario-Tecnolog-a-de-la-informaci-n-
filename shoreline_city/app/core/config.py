"""Configuración central de la aplicación.

Lee variables de entorno (o un archivo .env) mediante pydantic-settings.
Cumple RF-070 (parámetros configurables) y RNF-008 (mantenibilidad).
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    APP_NAME: str = "Shoreline City"
    ENVIRONMENT: str = "development"

    # Seguridad
    SECRET_KEY: str = "dev-secret-key-change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    COOKIE_SECURE: bool = False

    # Base de datos
    POSTGRES_USER: str = "shoreline"
    POSTGRES_PASSWORD: str = "shoreline_pass"
    POSTGRES_DB: str = "shoreline_city"
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str | None = None

    # Admin inicial
    FIRST_ADMIN_EMAIL: str = "admin@shorelinecity.org"
    FIRST_ADMIN_PASSWORD: str = "Admin1234"
    FIRST_ADMIN_NAME: str = "Administrador General"

    @property
    def sqlalchemy_url(self) -> str:
        """URL de conexión. Prioriza DATABASE_URL (útil para pruebas con SQLite)."""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            f"postgresql+psycopg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
