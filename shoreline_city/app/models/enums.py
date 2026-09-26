"""Enumeraciones y catálogos base del dominio."""
import enum


class EstadoPersona(str, enum.Enum):
    nuevo = "nuevo"
    activo = "activo"
    inactivo = "inactivo"
    visitante = "visitante"
    miembro = "miembro"


class EstadoServicio(str, enum.Enum):
    programado = "programado"
    en_curso = "en_curso"
    finalizado = "finalizado"
    cancelado = "cancelado"


class EstadoCheckIn(str, enum.Enum):
    registrado = "registrado"
    anulado = "anulado"


class EstadoCohorte(str, enum.Enum):
    abierta = "abierta"
    en_curso = "en_curso"
    finalizada = "finalizada"
    cancelada = "cancelada"


class EstadoInscripcion(str, enum.Enum):
    inscrito = "inscrito"
    en_proceso = "en_proceso"
    completado = "completado"
    integrado = "integrado"
    retirado = "retirado"


class EstadoFormulario(str, enum.Enum):
    borrador = "borrador"
    publicado = "publicado"
    cerrado = "cerrado"


# Permisos del sistema (RF-057). Formato: "modulo:accion".
ACCIONES = ["ver", "crear", "editar", "eliminar", "exportar"]
MODULOS = [
    "personas", "checkin", "nametags", "unete", "conteos",
    "servicios", "analiticas", "formularios", "voluntariado",
    "usuarios", "auditoria", "configuracion",
]


def todos_los_permisos() -> list[str]:
    return [f"{m}:{a}" for m in MODULOS for a in ACCIONES]
