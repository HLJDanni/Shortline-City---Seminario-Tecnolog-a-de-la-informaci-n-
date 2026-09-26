"""Módulo Personas: núcleo del sistema (RF-001 a RF-010).

La Persona mantiene el mismo ID en todos los módulos (RF-069).
"""
from datetime import date, datetime

from sqlalchemy import (
    JSON, Boolean, Date, DateTime, ForeignKey, Integer, String, Table, Column, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import EstadoPersona

# Relación N:M entre personas y etiquetas (RF-008).
persona_etiqueta = Table(
    "persona_etiqueta",
    Base.metadata,
    Column("persona_id", ForeignKey("personas.id", ondelete="CASCADE"), primary_key=True),
    Column("etiqueta_id", ForeignKey("etiquetas.id", ondelete="CASCADE"), primary_key=True),
)


class Familia(Base):
    """Unidad familiar para agrupar personas (RF-007)."""
    __tablename__ = "familias"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    creada_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    integrantes: Mapped[list["Persona"]] = relationship(back_populates="familia")


class Etiqueta(Base):
    """Etiquetas configurables para segmentar (RF-008)."""
    __tablename__ = "etiquetas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    color: Mapped[str] = mapped_column(String(20), default="#0d6efd")

    personas: Mapped[list["Persona"]] = relationship(
        secondary=persona_etiqueta, back_populates="etiquetas"
    )


class Persona(Base):
    __tablename__ = "personas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombres: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    apellidos: Mapped[str] = mapped_column(String(120), default="", index=True)
    telefono: Mapped[str | None] = mapped_column(String(30), index=True, nullable=True)
    correo: Mapped[str | None] = mapped_column(String(160), index=True, nullable=True)
    direccion: Mapped[str | None] = mapped_column(String(255), nullable=True)
    fecha_nacimiento: Mapped[date | None] = mapped_column(Date, nullable=True)
    genero: Mapped[str | None] = mapped_column(String(20), nullable=True)
    estado: Mapped[str] = mapped_column(String(20), default=EstadoPersona.nuevo.value)
    notas: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    campos_extra: Mapped[dict] = mapped_column(JSON, default=dict)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    familia_id: Mapped[int | None] = mapped_column(ForeignKey("familias.id"), nullable=True)
    creada_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    actualizada_en: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    familia: Mapped[Familia | None] = relationship(back_populates="integrantes")
    etiquetas: Mapped[list[Etiqueta]] = relationship(
        secondary=persona_etiqueta, back_populates="personas"
    )
    historial: Mapped[list["HistorialPersona"]] = relationship(
        back_populates="persona", cascade="all, delete-orphan",
        order_by="desc(HistorialPersona.fecha)",
    )

    @property
    def nombre_completo(self) -> str:
        return f"{self.nombres} {self.apellidos}".strip()


class HistorialPersona(Base):
    """Historial de cambios y eventos por persona (RF-009)."""
    __tablename__ = "historial_persona"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    persona_id: Mapped[int] = mapped_column(ForeignKey("personas.id", ondelete="CASCADE"))
    usuario_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"), nullable=True)
    accion: Mapped[str] = mapped_column(String(80), nullable=False)
    detalle: Mapped[str] = mapped_column(String(500), default="")
    fecha: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    persona: Mapped[Persona] = relationship(back_populates="historial")
