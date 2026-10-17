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
    # Protección contra fuerza bruta en el login.
    LOGIN_MAX_INTENTOS: int = 5
    LOGIN_BLOQUEO_MINUTOS: int = 15

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


    @property
    def es_produccion(self) -> bool:
        return self.ENVIRONMENT.lower() in ("production", "produccion", "prod")

    def validar_produccion(self) -> None:
        """Impide arrancar en producción con secretos débiles o por defecto."""
        if not self.es_produccion:
            return
        errores = []
        if len(self.SECRET_KEY) < 32 or "change" in self.SECRET_KEY or "cambia" in self.SECRET_KEY:
            errores.append("SECRET_KEY debe ser aleatoria y de al menos 32 caracteres")
        if self.FIRST_ADMIN_PASSWORD == "Admin1234" or len(self.FIRST_ADMIN_PASSWORD) < 12:
            errores.append("FIRST_ADMIN_PASSWORD debe cambiarse (mínimo 12 caracteres)")
        if errores:
            raise RuntimeError("Configuración insegura para producción: " + "; ".join(errores))
        # En producción la cookie de sesión siempre viaja solo por HTTPS.
        self.COOKIE_SECURE = True


@lru_cache
def get_settings() -> Settings:
    s = Settings()
    s.validar_produccion()
    return s


settings = get_settings()
