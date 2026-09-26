"""Servicios, Check-in y Name Tags (RF-011 a RF-020, RF-034/035)."""
from datetime import date, datetime, time

from sqlalchemy import (
    JSON, Boolean, Date, DateTime, ForeignKey, Integer, String, Time, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import EstadoCheckIn, EstadoServicio


class Servicio(Base):
    __tablename__ = "servicios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    fecha: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    hora: Mapped[time | None] = mapped_column(Time, nullable=True)
    ubicacion: Mapped[str | None] = mapped_column(String(160), nullable=True)
    tipo: Mapped[str] = mapped_column(String(60), default="regular")
    especial: Mapped[bool] = mapped_column(Boolean, default=False)  # RF-035
    estado: Mapped[str] = mapped_column(String(20), default=EstadoServicio.programado.value)
    creado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    checkins: Mapped[list["CheckIn"]] = relationship(back_populates="servicio")
    conteos: Mapped[list["Conteo"]] = relationship(back_populates="servicio")


class CheckIn(Base):
    __tablename__ = "checkins"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    persona_id: Mapped[int] = mapped_column(ForeignKey("personas.id"), nullable=False)
    servicio_id: Mapped[int] = mapped_column(ForeignKey("servicios.id"), nullable=False)
    operador_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"), nullable=True)
    fecha_hora: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    estado: Mapped[str] = mapped_column(String(20), default=EstadoCheckIn.registrado.value)
    motivo_correccion: Mapped[str | None] = mapped_column(String(255), nullable=True)

    persona: Mapped["Persona"] = relationship()  # noqa: F821
    servicio: Mapped[Servicio] = relationship(back_populates="checkins")


class PlantillaNameTag(Base):
    """Plantilla configurable de gafete (RF-017)."""
    __tablename__ = "plantillas_nametag"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(80), nullable=False)
    # Campos a mostrar: ["nombre", "rol", "equipo", "fecha", ...]
    campos: Mapped[list] = mapped_column(JSON, default=lambda: ["nombre", "fecha"])
    activa: Mapped[bool] = mapped_column(Boolean, default=True)


class NameTag(Base):
    """Impresión de gafete (RF-018 a RF-020)."""
    __tablename__ = "nametags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    persona_id: Mapped[int] = mapped_column(ForeignKey("personas.id"), nullable=False)
    plantilla_id: Mapped[int] = mapped_column(ForeignKey("plantillas_nametag.id"))
    servicio_id: Mapped[int | None] = mapped_column(ForeignKey("servicios.id"), nullable=True)
    impresora: Mapped[str | None] = mapped_column(String(120), nullable=True)
    reimpresion: Mapped[bool] = mapped_column(Boolean, default=False)  # RF-020
    fecha: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    persona: Mapped["Persona"] = relationship()  # noqa: F821
    plantilla: Mapped[PlantillaNameTag] = relationship()
