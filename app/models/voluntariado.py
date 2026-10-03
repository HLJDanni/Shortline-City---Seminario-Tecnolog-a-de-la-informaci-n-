"""Voluntariado: equipos, roles y asignaciones (RF-051 a RF-054)."""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Equipo(Base):
    __tablename__ = "equipos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    roles: Mapped[list["RolEquipo"]] = relationship(
        back_populates="equipo", cascade="all, delete-orphan"
    )
    asignaciones: Mapped[list["Asignacion"]] = relationship(back_populates="equipo")


class RolEquipo(Base):
    __tablename__ = "roles_equipo"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    equipo_id: Mapped[int] = mapped_column(ForeignKey("equipos.id", ondelete="CASCADE"))
    nombre: Mapped[str] = mapped_column(String(80), nullable=False)

    equipo: Mapped[Equipo] = relationship(back_populates="roles")


class Asignacion(Base):
    __tablename__ = "asignaciones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    persona_id: Mapped[int] = mapped_column(ForeignKey("personas.id"), nullable=False)
    equipo_id: Mapped[int] = mapped_column(ForeignKey("equipos.id"), nullable=False)
    rol_equipo_id: Mapped[int | None] = mapped_column(ForeignKey("roles_equipo.id"), nullable=True)
    servicio_id: Mapped[int | None] = mapped_column(ForeignKey("servicios.id"), nullable=True)
    disponibilidad: Mapped[str | None] = mapped_column(String(255), nullable=True)  # RF-054
    activa: Mapped[bool] = mapped_column(Boolean, default=True)
    creada_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    persona: Mapped["Persona"] = relationship()  # noqa: F821
    equipo: Mapped[Equipo] = relationship(back_populates="asignaciones")
    rol_equipo: Mapped[RolEquipo | None] = relationship()
