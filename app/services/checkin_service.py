"""Lógica de Check-in y conteos (RF-012 a RF-016, RF-029 a RF-033)."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import CheckIn, Conteo, ConteoDetalle, EstadoCheckIn
from app.services import auditoria_service as audit


def registrar_checkin(db: Session, persona_id: int, servicio_id: int,
                      operador_id: int | None = None) -> tuple[CheckIn, bool]:
    """RF-012. Evita duplicar el registro activo de la misma persona/servicio.

    Devuelve (checkin, creado). Si ya existía uno activo, creado=False.
    """
    existente = db.scalar(
        select(CheckIn).where(
            CheckIn.persona_id == persona_id,
            CheckIn.servicio_id == servicio_id,
            CheckIn.estado == EstadoCheckIn.registrado.value,
        )
    )
    if existente:
        return existente, False

    ci = CheckIn(persona_id=persona_id, servicio_id=servicio_id, operador_id=operador_id)
    db.add(ci)
    db.commit()
    db.refresh(ci)
    audit.registrar_historial(db, persona_id, "checkin",
                              f"Check-in en servicio {servicio_id}", operador_id, commit=False)
    audit.registrar(db, "checkin", operador_id, "CheckIn", ci.id,
                    f"Persona {persona_id} en servicio {servicio_id}")
    return ci, True


def anular_checkin(db: Session, checkin: CheckIn, motivo: str,
                   usuario_id: int | None = None) -> CheckIn:
    """RF-016: corrección/anulación con auditoría."""
    checkin.estado = EstadoCheckIn.anulado.value
    checkin.motivo_correccion = motivo
    db.commit()
    audit.registrar(db, "anular_checkin", usuario_id, "CheckIn", checkin.id, motivo)
    return checkin


def guardar_conteo(db: Session, servicio_id: int, detalles: list[dict],
                   responsable_id: int | None = None) -> Conteo:
    """RF-029 a RF-032: guarda un conteo y calcula el total automáticamente."""
    conteo = Conteo(servicio_id=servicio_id, responsable_id=responsable_id)
    db.add(conteo)
    db.flush()
    for d in detalles:
        conteo.detalles.append(
            ConteoDetalle(categoria_id=d["categoria_id"], cantidad=int(d["cantidad"]))
        )
    conteo.recalcular_total()  # RF-031
    db.commit()
    db.refresh(conteo)
    audit.registrar(db, "conteo", responsable_id, "Conteo", conteo.id,
                    f"Total {conteo.total} en servicio {servicio_id}")
    return conteo
