"""Usuarios, roles y permisos (RF-055 a RF-057)."""
from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Rol(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    descripcion: Mapped[str] = mapped_column(String(255), default="")
    # Lista de permisos "modulo:accion" (RF-057). "*" = acceso total.
    permisos: Mapped[list] = mapped_column(JSON, default=list)
    sistema: Mapped[bool] = mapped_column(Boolean, default=False)

    usuarios: Mapped[list["Usuario"]] = relationship(back_populates="rol")


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(160), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    rol_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False)
    creado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    ultimo_acceso: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    rol: Mapped[Rol] = relationship(back_populates="usuarios")

    def tiene_permiso(self, permiso: str) -> bool:
        """Verifica un permiso 'modulo:accion' respetando el comodín '*'."""
        permisos = self.rol.permisos or []
        if "*" in permisos or permiso in permisos:
            return True
        modulo = permiso.split(":", 1)[0]
        return f"{modulo}:*" in permisos
