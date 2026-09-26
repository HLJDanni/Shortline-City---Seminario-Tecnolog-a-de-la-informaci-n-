"""Pruebas de autenticación y RBAC (RF-055, RF-057, RNF-001)."""


def test_login_exitoso(client):
    r = client.post("/api/auth/login",
                    json={"email": "admin@shorelinecity.org", "password": "Admin1234"})
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_login_credenciales_invalidas(client):
    r = client.post("/api/auth/login",
                    json={"email": "admin@shorelinecity.org", "password": "malaclave"})
    assert r.status_code == 401


def test_acceso_sin_token_rechazado(client):
    r = client.get("/api/personas")
    assert r.status_code == 401


def test_me_devuelve_rol_y_permisos(client, admin_headers):
    r = client.get("/api/auth/me", headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["rol"] == "Administrador"
    assert "*" in r.json()["permisos"]


def test_password_nunca_en_texto_plano(db):
    """RNF-001: la contraseña se almacena con hash."""
    from sqlalchemy import select

    from app.models import Usuario

    admin = db.scalar(select(Usuario).where(Usuario.email == "admin@shorelinecity.org"))
    assert admin.hashed_password != "Admin1234"
    assert admin.hashed_password.startswith("$2")  # bcrypt


def test_rbac_usher_no_puede_crear_personas(client, usher_headers):
    """RNF-003: mínimo privilegio. Usher no tiene 'personas:crear'."""
    r = client.post("/api/personas",
                    json={"nombres": "Test", "apellidos": "Bloqueado"},
                    headers=usher_headers)
    assert r.status_code == 403


def test_rbac_usher_si_puede_ver_personas(client, usher_headers):
    r = client.get("/api/personas", headers=usher_headers)
    assert r.status_code == 200
