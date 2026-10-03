"""Conteos de Ushers (RF-029 a RF-033)."""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class CategoriaConteo(Base):
    """Categorías configurables de conteo (RF-030)."""
    __tablename__ = "categorias_conteo"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    activa: Mapped[bool] = mapped_column(Boolean, default=True)


class Conteo(Base):
    __tablename__ = "conteos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    servicio_id: Mapped[int] = mapped_column(ForeignKey("servicios.id"), nullable=False)
    responsable_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"), nullable=True)
    fecha_hora: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    total: Mapped[int] = mapped_column(Integer, default=0)  # RF-031

    servicio: Mapped["Servicio"] = relationship(back_populates="conteos")  # noqa: F821
    detalles: Mapped[list["ConteoDetalle"]] = relationship(
        back_populates="conteo", cascade="all, delete-orphan"
    )

    def recalcular_total(self) -> int:
        self.total = sum(d.cantidad for d in self.detalles)
        return self.total


class ConteoDetalle(Base):
    __tablename__ = "conteo_detalle"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    conteo_id: Mapped[int] = mapped_column(ForeignKey("conteos.id", ondelete="CASCADE"))
    categoria_id: Mapped[int] = mapped_column(ForeignKey("categorias_conteo.id"))
    cantidad: Mapped[int] = mapped_column(Integer, default=0)
    # Auditoría de corrección (RF-033)
    valor_anterior: Mapped[int | None] = mapped_column(Integer, nullable=True)
    motivo_correccion: Mapped[str | None] = mapped_column(String(255), nullable=True)

    conteo: Mapped[Conteo] = relationship(back_populates="detalles")
    categoria: Mapped[CategoriaConteo] = relationship()
