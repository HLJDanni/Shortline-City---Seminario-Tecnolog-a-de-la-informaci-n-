"""API de servicios, check-in, conteos y analíticas (MVP)."""
from datetime import datetime, time
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import CurrentUser, require_permission
from app.models import CategoriaConteo, CheckIn, Cohorte, Conteo, Persona, Servicio
from app.schemas import (
    CheckInCreate, CheckInOut, ConteoCreate, ConteoOut,
    ServicioCreate, ServicioOut,
)
from app.services import analitica_service as anal
from app.services import checkin_service as ci_svc

router = APIRouter(prefix="/api", tags=["operacion"])


# ------------------------------ Servicios ------------------------------
@router.get("/servicios", response_model=list[ServicioOut])
def listar_servicios(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_permission("servicios:ver"))],
):
    return list(db.scalars(select(Servicio).order_by(Servicio.fecha.desc())).all())


@router.post("/servicios", response_model=ServicioOut,
             status_code=status.HTTP_201_CREATED)
def crear_servicio(
    datos: ServicioCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[CurrentUser, Depends(require_permission("servicios:crear"))],
):
    hora = None
    if datos.hora:
        try:
            hora = time.fromisoformat(datos.hora)
        except ValueError:
            raise HTTPException(422, "Hora inválida (use HH:MM)")
    servicio = Servicio(
        nombre=datos.nombre, fecha=datos.fecha, hora=hora,
        ubicacion=datos.ubicacion, tipo=datos.tipo, especial=datos.especial,
    )
    db.add(servicio)
    db.commit()
    db.refresh(servicio)
    return servicio


# ------------------------------ Check-in -------------------------------
@router.post("/checkin", response_model=CheckInOut,
             status_code=status.HTTP_201_CREATED)
def hacer_checkin(
    datos: CheckInCreate,
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[CurrentUser, Depends(require_permission("checkin:crear"))],
):
    if not db.get(Persona, datos.persona_id):
        raise HTTPException(404, "Persona no encontrada")
    if not db.get(Servicio, datos.servicio_id):
        raise HTTPException(404, "Servicio no encontrado")
    ci, _creado = ci_svc.registrar_checkin(
        db, datos.persona_id, datos.servicio_id, usuario.id
    )
    return ci


@router.get("/checkin/servicio/{servicio_id}", response_model=list[CheckInOut])
def checkins_de_servicio(
    servicio_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_permission("checkin:ver"))],
):
    return list(db.scalars(
        select(CheckIn).where(CheckIn.servicio_id == servicio_id)
    ).all())


# ------------------------------- Conteos -------------------------------
@router.post("/conteos", response_model=ConteoOut,
             status_code=status.HTTP_201_CREATED)
def crear_conteo(
    datos: ConteoCreate,
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[CurrentUser, Depends(require_permission("conteos:crear"))],
):
    if not db.get(Servicio, datos.servicio_id):
        raise HTTPException(404, "Servicio no encontrado")
    detalles = [d.model_dump() for d in datos.detalles]
    conteo = ci_svc.guardar_conteo(db, datos.servicio_id, detalles, usuario.id)
    return conteo


@router.get("/conteos")
def listar_conteos(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_permission("conteos:ver"))],
    limit: int = 20,
):
    filas = db.scalars(
        select(Conteo).order_by(Conteo.fecha_hora.desc()).limit(limit)
    ).all()
    return [
        {"id": c.id, "servicio_id": c.servicio_id, "total": c.total,
         "fecha_hora": c.fecha_hora.isoformat(),
         "servicio": c.servicio.nombre if c.servicio else None}
        for c in filas
    ]


@router.get("/conteos/categorias")
def listar_categorias(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_permission("conteos:ver"))],
):
    cats = db.scalars(
        select(CategoriaConteo).where(CategoriaConteo.activa.is_(True))
    ).all()
    return [{"id": c.id, "nombre": c.nombre} for c in cats]


# -------------------------------- Únete --------------------------------
@router.get("/unete/cohortes")
def listar_cohortes(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_permission("unete:ver"))],
):
    cohortes = db.scalars(select(Cohorte).order_by(Cohorte.creada_en.desc())).all()
    return [
        {"id": c.id, "nombre": c.nombre,
         "fecha_inicio": c.fecha_inicio.isoformat() if c.fecha_inicio else None,
         "horario": c.horario, "ubicacion": c.ubicacion, "estado": c.estado,
         "inscritos": len(c.inscripciones)}
        for c in cohortes
    ]


# ------------------------------ Analíticas -----------------------------
@router.get("/analiticas/resumen")
def resumen(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_permission("analiticas:ver"))],
):
    return {
        "kpis": anal.kpis_generales(db),
        "asistencia_por_servicio": anal.asistencia_por_servicio(db),
        "embudo_unete": anal.embudo_unete(db),
        "asistencia_total_conteos": anal.totales_conteos(db),
    }
