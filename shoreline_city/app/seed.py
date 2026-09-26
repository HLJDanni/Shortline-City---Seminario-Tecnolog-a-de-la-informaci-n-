"""Sembrado inicial de datos: roles, admin, catálogos (RF-056, RF-070)."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password
from app.models import (
    CategoriaConteo, PlantillaNameTag, Rol, Usuario, todos_los_permisos,
)

# Roles definidos en la hoja "Roles y permisos" del Excel.
ROLES_BASE = {
    "Administrador": {
        "descripcion": "Acceso total; configuración, usuarios, reportes y auditoría.",
        "permisos": ["*"],
        "sistema": True,
    },
    "Coordinador": {
        "descripcion": "Gestión operativa de personas, Únete, formularios, servicios y reportes.",
        "permisos": [
            "personas:ver", "personas:crear", "personas:editar", "personas:exportar",
            "checkin:ver", "checkin:crear",
            "unete:ver", "unete:crear", "unete:editar",
            "servicios:ver", "servicios:crear",
            "conteos:ver", "analiticas:ver",
            "formularios:ver", "formularios:crear", "formularios:editar",
            "voluntariado:ver", "voluntariado:crear", "voluntariado:editar",
        ],
    },
    "Líder": {
        "descripcion": "Acceso limitado a personas/equipos y seguimientos asignados.",
        "permisos": ["personas:ver", "unete:ver", "unete:editar",
                     "voluntariado:ver", "checkin:ver"],
    },
    "Usher": {
        "descripcion": "Conteos y funciones de Check-in autorizadas.",
        "permisos": ["checkin:ver", "checkin:crear", "conteos:ver", "conteos:crear",
                     "personas:ver", "servicios:ver"],
    },
    "Operador": {
        "descripcion": "Check-in, búsqueda y Name Tags.",
        "permisos": ["personas:ver", "personas:crear", "checkin:ver", "checkin:crear",
                     "nametags:ver", "nametags:crear", "servicios:ver"],
    },
    "Administrador técnico": {
        "descripcion": "Infraestructura, backups, API, integraciones y mantenimiento.",
        "permisos": ["*"],
        "sistema": True,
    },
}

CATEGORIAS_CONTEO = ["Adultos", "Jóvenes", "Niños", "Voluntarios"]


def sembrar(db: Session) -> None:
    # Roles
    roles: dict[str, Rol] = {}
    for nombre, cfg in ROLES_BASE.items():
        rol = db.scalar(select(Rol).where(Rol.nombre == nombre))
        if not rol:
            rol = Rol(nombre=nombre, descripcion=cfg["descripcion"],
                      permisos=cfg["permisos"], sistema=cfg.get("sistema", False))
            db.add(rol)
        roles[nombre] = rol
    db.commit()

    # Usuario administrador inicial
    admin = db.scalar(select(Usuario).where(Usuario.email == settings.FIRST_ADMIN_EMAIL.lower()))
    if not admin:
        db.add(Usuario(
            nombre=settings.FIRST_ADMIN_NAME,
            email=settings.FIRST_ADMIN_EMAIL.lower(),
            hashed_password=hash_password(settings.FIRST_ADMIN_PASSWORD),
            rol_id=roles["Administrador"].id,
        ))

    # Categorías de conteo
    for nombre in CATEGORIAS_CONTEO:
        if not db.scalar(select(CategoriaConteo).where(CategoriaConteo.nombre == nombre)):
            db.add(CategoriaConteo(nombre=nombre))

    # Plantilla de Name Tag por defecto
    if not db.scalar(select(PlantillaNameTag)):
        db.add(PlantillaNameTag(nombre="Estándar",
                                campos=["nombre", "rol", "fecha"]))
    db.commit()


def _todos_permisos_disponibles() -> list[str]:
    """Utilidad para pantallas de configuración de roles (RF-056)."""
    return ["*"] + todos_los_permisos()
