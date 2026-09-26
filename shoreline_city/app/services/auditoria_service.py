"""Servicio de auditoría e historial (RF-058, RF-009)."""
from sqlalchemy.orm import Session

from app.models import Auditoria, HistorialPersona


def registrar(
    db: Session,
    accion: str,
    usuario_id: int | None = None,
    entidad: str | None = None,
    entidad_id: str | int | None = None,
    detalle: str = "",
    ip: str | None = None,
    commit: bool = True,
) -> Auditoria:
    evento = Auditoria(
        usuario_id=usuario_id,
        accion=accion,
        entidad=entidad,
        entidad_id=str(entidad_id) if entidad_id is not None else None,
        detalle=detalle[:600],
        ip=ip,
    )
    db.add(evento)
    if commit:
        db.commit()
    return evento


def registrar_historial(
    db: Session,
    persona_id: int,
    accion: str,
    detalle: str = "",
    usuario_id: int | None = None,
    commit: bool = True,
) -> HistorialPersona:
    h = HistorialPersona(
        persona_id=persona_id, accion=accion,
        detalle=detalle[:500], usuario_id=usuario_id,
    )
    db.add(h)
    if commit:
        db.commit()
    return h
