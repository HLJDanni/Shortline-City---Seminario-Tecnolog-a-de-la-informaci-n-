"""Formularios dinámicos (RF-043 a RF-050)."""
from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    JSON, Boolean, DateTime, ForeignKey, Integer, String, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import EstadoFormulario


def _slug() -> str:
    return uuid4().hex[:12]


class Formulario(Base):
    __tablename__ = "formularios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(160), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(String(500), nullable=True)
    estado: Mapped[str] = mapped_column(String(20), default=EstadoFormulario.borrador.value)
    slug: Mapped[str] = mapped_column(String(20), unique=True, default=_slug, index=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    campos: Mapped[list["CampoFormulario"]] = relationship(
        back_populates="formulario", cascade="all, delete-orphan",
        order_by="CampoFormulario.orden",
    )
    respuestas: Mapped[list["RespuestaFormulario"]] = relationship(
        back_populates="formulario", cascade="all, delete-orphan"
    )


class CampoFormulario(Base):
    __tablename__ = "campos_formulario"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    formulario_id: Mapped[int] = mapped_column(ForeignKey("formularios.id", ondelete="CASCADE"))
    etiqueta: Mapped[str] = mapped_column(String(160), nullable=False)
    # tipo: texto, numero, correo, telefono, fecha, seleccion, checkbox, archivo
    tipo: Mapped[str] = mapped_column(String(30), default="texto")
    requerido: Mapped[bool] = mapped_column(Boolean, default=False)  # RF-045
    opciones: Mapped[list] = mapped_column(JSON, default=list)
    orden: Mapped[int] = mapped_column(Integer, default=0)
    # Marca campos que se usan para vincular persona (RF-047)
    mapea_a: Mapped[str | None] = mapped_column(String(30), nullable=True)

    formulario: Mapped[Formulario] = relationship(back_populates="campos")


class RespuestaFormulario(Base):
    __tablename__ = "respuestas_formulario"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    formulario_id: Mapped[int] = mapped_column(ForeignKey("formularios.id", ondelete="CASCADE"))
    persona_id: Mapped[int | None] = mapped_column(ForeignKey("personas.id"), nullable=True)
    datos: Mapped[dict] = mapped_column(JSON, default=dict)
    fecha: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    formulario: Mapped[Formulario] = relationship(back_populates="respuestas")
    persona: Mapped["Persona"] = relationship()  # noqa: F821
