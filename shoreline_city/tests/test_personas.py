"""Pruebas del módulo Personas (RF-001 a RF-006, RF-009)."""


def _crear(client, headers, **kw):
    payload = {"nombres": "Juan", "apellidos": "Pérez"}
    payload.update(kw)
    return client.post("/api/personas", json=payload, headers=headers)


def test_crear_persona_genera_id(client, admin_headers):
    r = _crear(client, admin_headers)
    assert r.status_code == 201
    data = r.json()
    assert data["id"] > 0
    assert data["nombres"] == "Juan"


def test_crear_persona_requiere_nombre(client, admin_headers):
    r = client.post("/api/personas", json={"apellidos": "SinNombre"}, headers=admin_headers)
    assert r.status_code == 422  # validación RF-059


def test_deteccion_duplicado_por_telefono(client, admin_headers):
    _crear(client, admin_headers, telefono="5555-1111")
    # Mismo teléfono, distinto nombre -> alerta de duplicado (RF-006)
    r = _crear(client, admin_headers, nombres="Otro", apellidos="Nombre",
               telefono="5555-1111")
    assert r.status_code == 409
    assert r.json()["detail"]["duplicado"] is True


def test_forzar_creacion_ignora_duplicado(client, admin_headers):
    _crear(client, admin_headers, telefono="5555-2222")
    r = _crear(client, admin_headers, nombres="Otro", telefono="5555-2222", forzar=True)
    assert r.status_code == 201


def test_editar_persona_actualiza(client, admin_headers):
    pid = _crear(client, admin_headers).json()["id"]
    r = client.put(f"/api/personas/{pid}", json={"estado": "miembro"},
                   headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["estado"] == "miembro"


def test_busqueda_por_texto(client, admin_headers):
    _crear(client, admin_headers, nombres="Mariana", apellidos="Solís")
    r = client.get("/api/personas?q=Mariana", headers=admin_headers)
    assert r.status_code == 200
    assert any("Mariana" in p["nombres"] for p in r.json())


def test_filtro_por_estado(client, admin_headers):
    _crear(client, admin_headers, nombres="Activo", estado="activo", forzar=True)
    r = client.get("/api/personas?estado=activo", headers=admin_headers)
    assert all(p["estado"] == "activo" for p in r.json())


def test_baja_logica_no_aparece(client, admin_headers):
    pid = _crear(client, admin_headers, nombres="Baja").json()["id"]
    assert client.delete(f"/api/personas/{pid}", headers=admin_headers).status_code == 204
    r = client.get(f"/api/personas/{pid}", headers=admin_headers)
    assert r.status_code == 404


def test_historial_registra_creacion(client, admin_headers, db):
    from sqlalchemy import select

    from app.models import HistorialPersona

    pid = _crear(client, admin_headers, nombres="ConHistorial").json()["id"]
    eventos = db.scalars(
        select(HistorialPersona).where(HistorialPersona.persona_id == pid)
    ).all()
    assert any(e.accion == "creacion" for e in eventos)
