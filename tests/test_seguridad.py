"""Pruebas de seguridad de la sesión: cookie HttpOnly, logout, fuerza bruta,
cabeceras HTTP y validación de configuración (RNF-001, RNF-002, RNF-003)."""
import pytest

ADMIN = {"email": "admin@shorelinecity.org", "password": "Admin1234"}


def test_login_fija_cookie_httponly_samesite(client):
    r = client.post("/api/auth/login", json=ADMIN)
    assert r.status_code == 200
    cookie = r.headers["set-cookie"].lower()
    assert "access_token=" in cookie
    assert "httponly" in cookie
    assert "samesite=strict" in cookie


def test_cookie_basta_para_autenticar(client):
    client.post("/api/auth/login", json=ADMIN)
    r = client.get("/api/auth/me")  # sin header Authorization
    assert r.status_code == 200
    assert r.json()["email"] == ADMIN["email"]


def test_logout_revoca_token_y_borra_cookie(client):
    token = client.post("/api/auth/login", json=ADMIN).json()["access_token"]
    r = client.post("/api/auth/logout")
    assert r.status_code == 204
    assert client.get("/api/auth/me").status_code == 401
    # El mismo token, usado como Bearer, también quedó revocado.
    r = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 401


def test_token_alterado_rechazado(client):
    token = client.post("/api/auth/login", json=ADMIN).json()["access_token"]
    client.cookies.clear()
    malo = token[:-3] + ("aaa" if not token.endswith("aaa") else "bbb")
    r = client.get("/api/auth/me", headers={"Authorization": f"Bearer {malo}"})
    assert r.status_code == 401


def test_token_alg_none_rechazado(client):
    from jose import jwt

    falso = jwt.encode({"sub": "1", "iss": "shoreline-city"}, key="", algorithm="HS256")
    r = client.get("/api/auth/me", headers={"Authorization": f"Bearer {falso}"})
    assert r.status_code == 401


def test_bloqueo_por_intentos_fallidos(client):
    from app.core.config import settings

    for _ in range(settings.LOGIN_MAX_INTENTOS):
        r = client.post("/api/auth/login",
                        json={"email": ADMIN["email"], "password": "incorrecta"})
        assert r.status_code == 401
    # Ni siquiera la contraseña correcta entra mientras dura el bloqueo.
    r = client.post("/api/auth/login", json=ADMIN)
    assert r.status_code == 429
    assert "Retry-After" in r.headers


def test_cabeceras_de_seguridad(client):
    r = client.get("/health")
    assert r.headers["X-Content-Type-Options"] == "nosniff"
    assert r.headers["X-Frame-Options"] == "DENY"
    assert "default-src 'self'" in r.headers["Content-Security-Policy"]


def test_api_no_se_cachea(client, admin_headers):
    r = client.get("/api/auth/me", headers=admin_headers)
    assert r.headers["Cache-Control"] == "no-store"


def test_produccion_rechaza_secretos_por_defecto():
    from app.core.config import Settings

    s = Settings(ENVIRONMENT="production", SECRET_KEY="dev-secret-key-change-me",
                 FIRST_ADMIN_PASSWORD="Admin1234")
    with pytest.raises(RuntimeError):
        s.validar_produccion()


def test_produccion_fuerza_cookie_secure():
    from app.core.config import Settings

    s = Settings(ENVIRONMENT="production", SECRET_KEY="x" * 64,
                 FIRST_ADMIN_PASSWORD="UnaClaveLarga2026", COOKIE_SECURE=False)
    s.validar_produccion()
    assert s.COOKIE_SECURE is True
