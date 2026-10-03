"""Pruebas del serving del SPA y endpoints de apoyo del frontend."""


def test_health(client):
    assert client.get("/health").json()["status"] == "ok"


def test_api_requiere_auth(client):
    assert client.get("/api/personas").status_code == 401


def test_spa_fallback_no_es_404(client):
    """Las rutas de Vue Router deben resolver al index (200) o 503 si no hay
    build; nunca 404 (eso rompería el enrutamiento del cliente)."""
    r = client.get("/personas")
    assert r.status_code in (200, 503)


def test_ruta_api_desconocida_da_404(client):
    assert client.get("/api/no-existe").status_code == 404


def test_endpoint_cohortes(client, admin_headers):
    assert client.get("/api/unete/cohortes", headers=admin_headers).status_code == 200


def test_endpoint_listar_conteos(client, admin_headers):
    assert client.get("/api/conteos", headers=admin_headers).status_code == 200


def test_perfil_360(client, admin_headers):
    pid = client.post("/api/personas", json={"nombres": "Perfil", "forzar": True},
                      headers=admin_headers).json()["id"]
    r = client.get(f"/api/personas/{pid}/perfil", headers=admin_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["persona"]["id"] == pid
    assert "historial" in body and "checkins" in body
