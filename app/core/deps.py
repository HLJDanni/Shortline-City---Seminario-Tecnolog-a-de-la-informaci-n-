"""Dependencias de FastAPI para autenticación y autorización (RBAC).

Cumple RF-055 (autenticación), RF-057 (permisos por módulo/acción) y
RNF-003 (mínimo privilegio).
"""
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decodificar_token
from app.models import Usuario

COOKIE_NAME = "access_token"


class CredentialsError(HTTPException):
    """Se distingue para redirigir al login en rutas web."""

    def __init__(self, detail: str = "No autenticado"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


def _extraer_token(request: Request) -> str | None:
    # 1) Cookie (frontend web)
    token = request.cookies.get(COOKIE_NAME)
    if token:
        return token
    # 2) Header Authorization: Bearer (API / integraciones RF-065)
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth[7:]
    return None


def get_current_user(
    request: Request, db: Annotated[Session, Depends(get_db)]
) -> Usuario:
    token = _extraer_token(request)
    if not token:
        raise CredentialsError()
    payload = decodificar_token(token)
    if not payload or "sub" not in payload:
        raise CredentialsError("Token inválido o expirado")
    usuario = db.get(Usuario, int(payload["sub"]))
    if not usuario or not usuario.activo:
        raise CredentialsError("Usuario inactivo o inexistente")
    return usuario


CurrentUser = Annotated[Usuario, Depends(get_current_user)]


def require_permission(permiso: str):
    """Fábrica de dependencias que exige un permiso 'modulo:accion'."""

    def _checker(usuario: CurrentUser) -> Usuario:
        if not usuario.tiene_permiso(permiso):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permiso requerido: {permiso}",
            )
        return usuario

    return _checker
