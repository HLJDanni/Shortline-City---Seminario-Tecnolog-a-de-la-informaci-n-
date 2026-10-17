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
        """URL de conexión. Prioriza DATABASE_URL (Supabase, Render o SQLite).

        Acepta la cadena tal como la entrega Supabase (``postgresql://...``):
        se adapta al driver psycopg 3 y, si el host es de Supabase, se exige SSL.
        """
        if self.DATABASE_URL:
            url = self.DATABASE_URL.strip()
            for prefijo in ("postgres://", "postgresql://"):
                if url.startswith(prefijo):
                    url = "postgresql+psycopg://" + url[len(prefijo):]
                    break
            if "supabase." in url and "sslmode=" not in url:
                url += ("&" if "?" in url else "?") + "sslmode=require"
            return url
        return (
            f"postgresql+psycopg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
