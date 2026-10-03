"""Configuración de pruebas. Usa SQLite para ejecutarse sin PostgreSQL.

La aplicación usa PostgreSQL 18 en producción; los modelos emplean tipos
genéricos (incluido JSON) compatibles con ambos motores.
"""
import os

# Debe definirse ANTES de importar la app para que el engine use SQLite.
os.environ["DATABASE_URL"] = "sqlite:///./test_shoreline.db"
os.environ["SECRET_KEY"] = "test-secret"

import pytest
from fastapi.testclient import TestClient

from app.core.database import Base, SessionLocal, engine
from app.main import app
from app.seed import sembrar


@pytest.fixture()
def db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        sembrar(session)
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db):
    # TestClient sin lifespan: las tablas y el seed los prepara la fixture `db`.
    return TestClient(app)


def _login(client: TestClient, email: str, password: str) -> str:
    r = client.post("/api/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


@pytest.fixture()
def admin_headers(client):
    token = _login(client, "admin@shorelinecity.org", "Admin1234")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def usher_user(db):
    """Crea un usuario con rol Usher (permisos limitados) para probar RBAC."""
    from sqlalchemy import select

    from app.core.security import hash_password
    from app.models import Rol, Usuario

    rol = db.scalar(select(Rol).where(Rol.nombre == "Usher"))
    u = Usuario(nombre="Usher Test", email="usher@test.org",
                hashed_password=hash_password("Usher1234"), rol_id=rol.id)
    db.add(u)
    db.commit()
    return u


@pytest.fixture()
def usher_headers(client, usher_user):
    token = _login(client, "usher@test.org", "Usher1234")
    return {"Authorization": f"Bearer {token}"}
