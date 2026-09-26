"""Esquemas Pydantic v2 para validación de entrada/salida (RF-059, RNF-014)."""
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ----------------------------- Auth -----------------------------
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginIn(BaseModel):
    email: EmailStr
    password: str


# ---------------------------- Personas --------------------------
class PersonaBase(BaseModel):
    nombres: str = Field(min_length=1, max_length=120)
    apellidos: str = Field(default="", max_length=120)
    telefono: str | None = Field(default=None, max_length=30)
    correo: EmailStr | None = None
    direccion: str | None = None
    fecha_nacimiento: date | None = None
    genero: str | None = None
    estado: str = "nuevo"
    notas: str | None = None


class PersonaCreate(PersonaBase):
    forzar: bool = False  # ignora alerta de duplicados (RF-006)


class PersonaUpdate(BaseModel):
    nombres: str | None = Field(default=None, max_length=120)
    apellidos: str | None = Field(default=None, max_length=120)
    telefono: str | None = None
    correo: EmailStr | None = None
    direccion: str | None = None
    fecha_nacimiento: date | None = None
    genero: str | None = None
    estado: str | None = None
    notas: str | None = None


class EtiquetaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nombre: str
    color: str


class PersonaOut(PersonaBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    activo: bool
    creada_en: datetime
    etiquetas: list[EtiquetaOut] = []


class DuplicadoOut(BaseModel):
    """Respuesta cuando se detecta un posible duplicado (RF-006)."""
    duplicado: bool
    coincidencias: list[PersonaOut] = []


# ---------------------------- Servicios -------------------------
class ServicioCreate(BaseModel):
    nombre: str
    fecha: date
    hora: str | None = None
    ubicacion: str | None = None
    tipo: str = "regular"
    especial: bool = False


class ServicioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nombre: str
    fecha: date
    ubicacion: str | None
    tipo: str
    estado: str


# ----------------------------- Check-in -------------------------
class CheckInCreate(BaseModel):
    persona_id: int
    servicio_id: int


class CheckInOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    persona_id: int
    servicio_id: int
    fecha_hora: datetime
    estado: str


# ----------------------------- Conteo ---------------------------
class ConteoDetalleIn(BaseModel):
    categoria_id: int
    cantidad: int = Field(ge=0)


class ConteoCreate(BaseModel):
    servicio_id: int
    detalles: list[ConteoDetalleIn]


class ConteoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    servicio_id: int
    total: int
    fecha_hora: datetime
