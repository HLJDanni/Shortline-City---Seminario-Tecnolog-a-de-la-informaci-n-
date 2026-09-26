"""Lógica de negocio del módulo Personas (RF-001 a RF-010)."""
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models import Persona
from app.schemas import PersonaCreate, PersonaUpdate
from app.services import auditoria_service as audit


def detectar_duplicados(db: Session, nombres: str, apellidos: str = "",
                        telefono: str | None = None,
                        correo: str | None = None) -> list[Persona]:
    """RF-006: detecta posibles duplicados por teléfono, correo o nombre completo."""
    condiciones = []
    if telefono:
        condiciones.append(Persona.telefono == telefono)
    if correo:
        condiciones.append(Persona.correo == correo)
    # Nombre + apellido (coincidencia exacta, insensible a mayúsculas)
    condiciones.append(
        (Persona.nombres.ilike(nombres.strip()))
        & (Persona.apellidos.ilike((apellidos or "").strip()))
    )
    if not condiciones:
        return []
    stmt = select(Persona).where(Persona.activo.is_(True)).where(or_(*condiciones))
    return list(db.scalars(stmt).all())


def crear_persona(db: Session, datos: PersonaCreate,
                  usuario_id: int | None = None) -> tuple[Persona | None, list[Persona]]:
    """Crea una persona. Devuelve (persona, duplicados).

    Si hay duplicados y no se fuerza, devuelve (None, duplicados) sin crear.
    """
    dups = detectar_duplicados(
        db, datos.nombres, datos.apellidos, datos.telefono,
        str(datos.correo) if datos.correo else None,
    )
    if dups and not datos.forzar:
        return None, dups

    persona = Persona(
        nombres=datos.nombres.strip(),
        apellidos=(datos.apellidos or "").strip(),
        telefono=datos.telefono,
        correo=str(datos.correo) if datos.correo else None,
        direccion=datos.direccion,
        fecha_nacimiento=datos.fecha_nacimiento,
        genero=datos.genero,
        estado=datos.estado,
        notas=datos.notas,
    )
    db.add(persona)
    db.commit()
    db.refresh(persona)
    audit.registrar_historial(db, persona.id, "creacion",
                              "Persona creada", usuario_id, commit=False)
    audit.registrar(db, "crear", usuario_id, "Persona", persona.id,
                    f"Creó a {persona.nombre_completo}")
    return persona, []


def actualizar_persona(db: Session, persona: Persona, datos: PersonaUpdate,
                       usuario_id: int | None = None) -> Persona:
    cambios = datos.model_dump(exclude_unset=True)
    for campo, valor in cambios.items():
        setattr(persona, campo, str(valor) if campo == "correo" and valor else valor)
    db.commit()
    db.refresh(persona)
    audit.registrar_historial(
        db, persona.id, "edicion",
        f"Campos actualizados: {', '.join(cambios.keys())}", usuario_id, commit=False,
    )
    audit.registrar(db, "editar", usuario_id, "Persona", persona.id,
                    f"Editó a {persona.nombre_completo}")
    return persona


def buscar(db: Session, q: str | None = None, estado: str | None = None,
           etiqueta_id: int | None = None, limit: int = 100,
           offset: int = 0) -> list[Persona]:
    """RF-003 y RF-004: búsqueda por texto y filtros combinables."""
    stmt = select(Persona).where(Persona.activo.is_(True))
    if q:
        patron = f"%{q.strip()}%"
        stmt = stmt.where(or_(
            Persona.nombres.ilike(patron),
            Persona.apellidos.ilike(patron),
            Persona.telefono.ilike(patron),
            Persona.correo.ilike(patron),
        ))
    if estado:
        stmt = stmt.where(Persona.estado == estado)
    if etiqueta_id:
        stmt = stmt.where(Persona.etiquetas.any(id=etiqueta_id))
    stmt = stmt.order_by(Persona.nombres, Persona.apellidos).limit(limit).offset(offset)
    return list(db.scalars(stmt).all())
