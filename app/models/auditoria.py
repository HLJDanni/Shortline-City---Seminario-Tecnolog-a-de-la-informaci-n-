"""Registro de auditoría de acciones sensibles (RF-058, RNF-012)."""
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Auditoria(Base):
    __tablename__ = "auditoria"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    usuario_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"), nullable=True)
    accion: Mapped[str] = mapped_column(String(80), nullable=False)
    entidad: Mapped[str | None] = mapped_column(String(60), nullable=True)
    entidad_id: Mapped[str | None] = mapped_column(String(40), nullable=True)
    detalle: Mapped[str] = mapped_column(String(600), default="")
    ip: Mapped[str | None] = mapped_column(String(60), nullable=True)
    fecha: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)
