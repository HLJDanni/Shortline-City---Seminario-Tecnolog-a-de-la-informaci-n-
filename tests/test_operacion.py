"""Pruebas de servicios, check-in, conteos y analíticas
(RF-011, RF-012, RF-029 a RF-031, RF-036 a RF-040)."""


def _servicio(client, headers):
    r = client.post("/api/servicios",
                    json={"nombre": "Servicio Test", "fecha": "2026-01-04"},
                    headers=headers)
    assert r.status_code == 201, r.text
    return r.json()["id"]


def _persona(client, headers, nombres="Asistente"):
    return client.post("/api/personas", json={"nombres": nombres, "forzar": True},
                       headers=headers).json()["id"]


def test_crear_servicio(client, admin_headers):
    assert _servicio(client, admin_headers) > 0


def test_checkin_registra_asistencia(client, admin_headers):
    sid = _servicio(client, admin_headers)
    pid = _persona(client, admin_headers)
    r = client.post("/api/checkin", json={"persona_id": pid, "servicio_id": sid},
                    headers=admin_headers)
    assert r.status_code == 201
    assert r.json()["estado"] == "registrado"


def test_checkin_no_duplica(client, admin_headers):
    sid = _servicio(client, admin_headers)
    pid = _persona(client, admin_headers)
    payload = {"persona_id": pid, "servicio_id": sid}
    ci1 = client.post("/api/checkin", json=payload, headers=admin_headers).json()
    ci2 = client.post("/api/checkin", json=payload, headers=admin_headers).json()
    assert ci1["id"] == ci2["id"]  # el segundo devuelve el mismo registro


def test_checkin_persona_inexistente(client, admin_headers):
    sid = _servicio(client, admin_headers)
    r = client.post("/api/checkin", json={"persona_id": 99999, "servicio_id": sid},
                    headers=admin_headers)
    assert r.status_code == 404


def test_conteo_calcula_total(client, admin_headers):
    sid = _servicio(client, admin_headers)
    cats = client.get("/api/conteos/categorias", headers=admin_headers).json()
    detalles = [{"categoria_id": cats[0]["id"], "cantidad": 10},
                {"categoria_id": cats[1]["id"], "cantidad": 5}]
    r = client.post("/api/conteos", json={"servicio_id": sid, "detalles": detalles},
                    headers=admin_headers)
    assert r.status_code == 201
    assert r.json()["total"] == 15  # RF-031


def test_analiticas_resumen(client, admin_headers):
    sid = _servicio(client, admin_headers)
    pid = _persona(client, admin_headers, "KpiTest")
    client.post("/api/checkin", json={"persona_id": pid, "servicio_id": sid},
                headers=admin_headers)
    r = client.get("/api/analiticas/resumen", headers=admin_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["kpis"]["total_personas"] >= 1
    assert body["kpis"]["total_checkins"] >= 1
