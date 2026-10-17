"""Configuración de SQLAlchemy: engine, sesión y Base declarativa.

Soporta PostgreSQL (producción, RF-069) y SQLite (pruebas, RNF-009).
"""
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

_url = settings.sqlalchemy_url
if _url.startswith("sqlite"):
    # SQLite necesita check_same_thread=False para el TestClient.
    _connect_args = {"check_same_thread": False}
else:
    # Desactiva las sentencias preparadas automáticas de psycopg 3: son
    # incompatibles con el pooler de Supabase (Supavisor) en modo transacción
    # y no aportan nada relevante con el volumen de esta aplicación.
    _connect_args = {"prepare_threshold": None}

engine = create_engine(_url, pool_pre_ping=True, connect_args=_connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Base declarativa para todos los modelos ORM."""


def get_db() -> Generator[Session, None, None]:
    """Dependencia de FastAPI que provee una sesión por request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
