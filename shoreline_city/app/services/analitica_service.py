"""Analíticas y KPIs del dashboard (RF-036 a RF-042)."""
from datetime import date, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import (
    CheckIn, Cohorte, Conteo, EstadoCheckIn, EstadoInscripcion,
    InscripcionUnete, Persona, Servicio,
)


def kpis_generales(db: Session) -> dict:
    """RF-036: indicadores principales."""
    total_personas = db.scalar(
        select(func.count()).select_from(Persona).where(Persona.activo.is_(True))
    ) or 0
    hace_30 = date.today() - timedelta(days=30)
    nuevas = db.scalar(
        select(func.count()).select_from(Persona)
        .where(func.date(Persona.creada_en) >= hace_30)
    ) or 0
    servicios = db.scalar(select(func.count()).select_from(Servicio)) or 0
    checkins = db.scalar(
        select(func.count()).select_from(CheckIn)
        .where(CheckIn.estado == EstadoCheckIn.registrado.value)
    ) or 0
    cohortes_activas = db.scalar(
        select(func.count()).select_from(Cohorte).where(Cohorte.estado != "finalizada")
    ) or 0
    return {
        "total_personas": total_personas,
        "personas_nuevas_30d": nuevas,   # RF-039
        "total_servicios": servicios,
        "total_checkins": checkins,
        "cohortes_activas": cohortes_activas,
    }


def asistencia_por_servicio(db: Session, limite: int = 10) -> list[dict]:
    """RF-038: check-ins agrupados por servicio."""
    stmt = (
        select(Servicio.nombre, Servicio.fecha, func.count(CheckIn.id))
        .join(CheckIn, CheckIn.servicio_id == Servicio.id, isouter=True)
        .where(CheckIn.estado == EstadoCheckIn.registrado.value)
        .group_by(Servicio.id)
        .order_by(Servicio.fecha.desc())
        .limit(limite)
    )
    return [
        {"servicio": n, "fecha": str(f), "asistencia": c}
        for n, f, c in db.execute(stmt).all()
    ]


def embudo_unete(db: Session) -> dict:
    """RF-040: embudo por estado de inscripción."""
    stmt = (
        select(InscripcionUnete.estado, func.count(InscripcionUnete.id))
        .group_by(InscripcionUnete.estado)
    )
    conteo = {estado: c for estado, c in db.execute(stmt).all()}
    return {e.value: conteo.get(e.value, 0) for e in EstadoInscripcion}


def totales_conteos(db: Session) -> int:
    """Suma de asistencia registrada por Ushers."""
    return db.scalar(select(func.coalesce(func.sum(Conteo.total), 0))) or 0
