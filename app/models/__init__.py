"""Importa todos los modelos para que SQLAlchemy registre las tablas."""
from app.models.auditoria import Auditoria
from app.models.conteo import CategoriaConteo, Conteo, ConteoDetalle
from app.models.enums import (
    EstadoCheckIn, EstadoCohorte, EstadoFormulario, EstadoInscripcion,
    EstadoPersona, EstadoServicio, todos_los_permisos,
)
from app.models.formulario import CampoFormulario, Formulario, RespuestaFormulario
from app.models.persona import Etiqueta, Familia, HistorialPersona, Persona
from app.models.servicio import CheckIn, NameTag, PlantillaNameTag, Servicio
from app.models.unete import (
    AsistenciaUnete, Cohorte, EventoUnete, InscripcionUnete, SesionUnete,
)
from app.models.usuario import Rol, Usuario
from app.models.voluntariado import Asignacion, Equipo, RolEquipo

__all__ = [
    "Auditoria", "CategoriaConteo", "Conteo", "ConteoDetalle",
    "CampoFormulario", "Formulario", "RespuestaFormulario",
    "Etiqueta", "Familia", "HistorialPersona", "Persona",
    "CheckIn", "NameTag", "PlantillaNameTag", "Servicio",
    "AsistenciaUnete", "Cohorte", "EventoUnete", "InscripcionUnete", "SesionUnete",
    "Rol", "Usuario", "Asignacion", "Equipo", "RolEquipo",
    "EstadoCheckIn", "EstadoCohorte", "EstadoFormulario", "EstadoInscripcion",
    "EstadoPersona", "EstadoServicio", "todos_los_permisos",
]
