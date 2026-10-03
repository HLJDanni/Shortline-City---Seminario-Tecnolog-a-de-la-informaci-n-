"""Módulo Únete: cohortes, inscripciones, sesiones y asistencia (RF-021 a RF-028)."""
from datetime import date, datetime

from sqlalchemy import (
    Boolean, Date, DateTime, ForeignKey, Integer, String, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import EstadoCohorte, EstadoInscripcion


class Cohorte(Base):
    """Edición/clase de Únete (RF-021)."""
    __tablename__ = "cohortes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    fecha_inicio: Mapped[date | None] = mapped_column(Date, nullable=True)
    horario: Mapped[str | None] = mapped_column(String(120), nullable=True)
    ubicacion: Mapped[str | None] = mapped_column(String(160), nullable=True)
    responsable_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"), nullable=True)
    estado: Mapped[str] = mapped_column(String(20), default=EstadoCohorte.abierta.value)
    creada_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    inscripciones: Mapped[list["InscripcionUnete"]] = relationship(
        back_populates="cohorte", cascade="all, delete-orphan"
    )
    sesiones: Mapped[list["SesionUnete"]] = relationship(
        back_populates="cohorte", cascade="all, delete-orphan"
    )


class InscripcionUnete(Base):
    __tablename__ = "inscripciones_unete"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    persona_id: Mapped[int] = mapped_column(ForeignKey("personas.id"), nullable=False)
    cohorte_id: Mapped[int] = mapped_column(ForeignKey("cohortes.id", ondelete="CASCADE"))
    estado: Mapped[str] = mapped_column(String(20), default=EstadoInscripcion.inscrito.value)
    responsable_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"), nullable=True)
    notas: Mapped[str | None] = mapped_column(String(1000), nullable=True)  # RF-027
    creada_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    cohorte: Mapped[Cohorte] = relationship(back_populates="inscripciones")
    persona: Mapped["Persona"] = relationship()  # noqa: F821
    eventos: Mapped[list["EventoUnete"]] = relationship(
        back_populates="inscripcion", cascade="all, delete-orphan",
        order_by="EventoUnete.fecha",
    )


class SesionUnete(Base):
    __tablename__ = "sesiones_unete"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cohorte_id: Mapped[int] = mapped_column(ForeignKey("cohortes.id", ondelete="CASCADE"))
    numero: Mapped[int] = mapped_column(Integer, default=1)
    nombre: Mapped[str | None] = mapped_column(String(120), nullable=True)
    fecha: Mapped[date | None] = mapped_column(Date, nullable=True)

    cohorte: Mapped[Cohorte] = relationship(back_populates="sesiones")


class AsistenciaUnete(Base):
    __tablename__ = "asistencia_unete"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    inscripcion_id: Mapped[int] = mapped_column(
        ForeignKey("inscripciones_unete.id", ondelete="CASCADE")
    )
    sesion_id: Mapped[int] = mapped_column(ForeignKey("sesiones_unete.id", ondelete="CASCADE"))
    asistio: Mapped[bool] = mapped_column(Boolean, default=False)


class EventoUnete(Base):
    """Línea de tiempo de la inscripción (RF-028)."""
    __tablename__ = "eventos_unete"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    inscripcion_id: Mapped[int] = mapped_column(
        ForeignKey("inscripciones_unete.id", ondelete="CASCADE")
    )
    tipo: Mapped[str] = mapped_column(String(60), nullable=False)
    detalle: Mapped[str] = mapped_column(String(500), default="")
    fecha: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    inscripcion: Mapped[InscripcionUnete] = relationship(back_populates="eventos")
