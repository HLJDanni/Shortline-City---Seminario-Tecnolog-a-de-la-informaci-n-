"""Endpoints de autenticación (RF-055, RF-060)."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import CurrentUser
from app.core.security import crear_token, verify_password
from app.models import Usuario
from app.schemas import LoginIn, Token
from app.services import auditoria_service as audit

router = APIRouter(prefix="/api/auth", tags=["auth"])


def autenticar(db: Session, email: str, password: str) -> Usuario | None:
    usuario = db.scalar(select(Usuario).where(Usuario.email == email.lower()))
    if not usuario or not usuario.activo:
        return None
    if not verify_password(password, usuario.hashed_password):
        return None
    return usuario


@router.post("/login", response_model=Token)
def login(datos: LoginIn, request: Request, db: Annotated[Session, Depends(get_db)]):
    usuario = autenticar(db, datos.email, datos.password)
    if not usuario:
        audit.registrar(db, "login_fallido", None, "Usuario", None, datos.email,
                        ip=request.client.host if request.client else None)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
        )
    token = crear_token(usuario.id, {"rol": usuario.rol.nombre})
    audit.registrar(db, "login", usuario.id, "Usuario", usuario.id, "Inicio de sesión",
                    ip=request.client.host if request.client else None)
    return Token(access_token=token)


@router.get("/me")
def me(usuario: CurrentUser):
    return {
        "id": usuario.id,
        "nombre": usuario.nombre,
        "email": usuario.email,
        "rol": usuario.rol.nombre,
        "permisos": usuario.rol.permisos,
    }
