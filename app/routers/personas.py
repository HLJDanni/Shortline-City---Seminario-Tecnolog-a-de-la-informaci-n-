"""API del módulo Personas (RF-001 a RF-010)."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from sqlalchemy import select

from app.core.database import get_db
from app.core.deps import CurrentUser, require_permission
from app.models import CheckIn, Persona
from app.schemas import (
    DuplicadoOut, PersonaCreate, PersonaOut, PersonaUpdate,
)
from app.services import persona_service as svc

router = APIRouter(prefix="/api/personas", tags=["personas"])


def _obtener(db: Session, persona_id: int) -> Persona:
    persona = db.get(Persona, persona_id)
    if not persona or not persona.activo:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Persona no encontrada")
    return persona


@router.get("", response_model=list[PersonaOut])
def listar(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_permission("personas:ver"))],
    q: str | None = None,
    estado: str | None = None,
    etiqueta_id: int | None = None,
    limit: int = 100,
    offset: int = 0,
):
    return svc.buscar(db, q, estado, etiqueta_id, limit, offset)


@router.post("", status_code=status.HTTP_201_CREATED,
             responses={409: {"model": DuplicadoOut}})
def crear(
    datos: PersonaCreate,
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[CurrentUser, Depends(require_permission("personas:crear"))],
):
    persona, duplicados = svc.crear_persona(db, datos, usuario.id)
    if persona is None:
        # RF-006: alerta de duplicado antes de crear.
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "duplicado": True,
                "mensaje": "Posible duplicado. Envíe forzar=true para crear de todos modos.",
                "coincidencias": [
                    {"id": d.id, "nombre": d.nombre_completo,
                     "telefono": d.telefono, "correo": d.correo}
                    for d in duplicados
                ],
            },
        )
    return PersonaOut.model_validate(persona)


@router.get("/{persona_id}", response_model=PersonaOut)
def obtener(
    persona_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_permission("personas:ver"))],
):
    return _obtener(db, persona_id)


@router.get("/{persona_id}/perfil")
def perfil_360(
    persona_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_permission("personas:ver"))],
):
    """Perfil 360°: datos + asistencias + historial consolidado (RF-005)."""
    persona = _obtener(db, persona_id)
    checkins = db.scalars(
        select(CheckIn).where(CheckIn.persona_id == persona_id)
        .order_by(CheckIn.fecha_hora.desc())
    ).all()
    return {
        "persona": PersonaOut.model_validate(persona).model_dump(),
        "checkins": [
            {"id": c.id, "servicio_id": c.servicio_id,
             "fecha_hora": c.fecha_hora.isoformat(), "estado": c.estado}
            for c in checkins
        ],
        "historial": [
            {"accion": h.accion, "detalle": h.detalle, "fecha": h.fecha.isoformat()}
            for h in persona.historial
        ],
    }


@router.put("/{persona_id}", response_model=PersonaOut)
def actualizar(
    persona_id: int,
    datos: PersonaUpdate,
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[CurrentUser, Depends(require_permission("personas:editar"))],
):
    persona = _obtener(db, persona_id)
    return svc.actualizar_persona(db, persona, datos, usuario.id)


@router.delete("/{persona_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(
    persona_id: int,
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[CurrentUser, Depends(require_permission("personas:eliminar"))],
):
    """Baja lógica para conservar integridad referencial (RF-069)."""
    persona = _obtener(db, persona_id)
    persona.activo = False
    db.commit()
