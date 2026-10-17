"""Endpoints de autenticación (RF-055, RF-060).

La sesión del navegador viaja en una cookie HttpOnly + Secure + SameSite=Strict:
JavaScript no puede leer el token (mitiga XSS) y el navegador no lo envía desde
otros sitios (mitiga CSRF). Para integraciones (RF-065) el login también
devuelve el token para usarlo como `Authorization: Bearer`.
"""
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.deps import COOKIE_NAME, CurrentUser, extraer_token
from app.core.security import (
    control_intentos, crear_token, decodificar_token, hash_password,
    tokens_revocados, verify_password,
)
from app.models import Usuario
from app.schemas import LoginIn, Token
from app.services import auditoria_service as audit

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Hash ficticio: iguala el tiempo de respuesta cuando el correo no existe,
# para no revelar qué correos están registrados.
_HASH_FICTICIO = hash_password("usuario-inexistente")


def autenticar(db: Session, email: str, password: str) -> Usuario | None:
    usuario = db.scalar(select(Usuario).where(Usuario.email == email.lower()))
    if not usuario or not usuario.activo:
        verify_password(password, _HASH_FICTICIO)
        return None
    if not verify_password(password, usuario.hashed_password):
        return None
    return usuario


def _ip(request: Request) -> str:
    return request.client.host if request.client else "desconocida"


@router.post("/login", response_model=Token)
def login(datos: LoginIn, request: Request, response: Response,
          db: Annotated[Session, Depends(get_db)]):
    ip = _ip(request)
    claves = (f"email:{datos.email.lower()}", f"ip:{ip}")

    espera = control_intentos.bloqueado(*claves)
    if espera:
        audit.registrar(db, "login_bloqueado", None, "Usuario", None, datos.email, ip=ip)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Demasiados intentos fallidos. Intente de nuevo en {espera // 60 + 1} minutos.",
            headers={"Retry-After": str(espera)},
        )

    usuario = autenticar(db, datos.email, datos.password)
    if not usuario:
        control_intentos.fallo(*claves)
        audit.registrar(db, "login_fallido", None, "Usuario", None, datos.email, ip=ip)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
        )

    control_intentos.exito(*claves)
    usuario.ultimo_acceso = datetime.utcnow()
    token = crear_token(usuario.id, {"rol": usuario.rol.nombre})
    audit.registrar(db, "login", usuario.id, "Usuario", usuario.id, "Inicio de sesión", ip=ip)

    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,                    # inaccesible para JavaScript
        secure=settings.COOKIE_SECURE,    # solo por HTTPS en producción
        samesite="strict",                # no se envía desde otros sitios
        path="/",
    )
    return Token(access_token=token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request, response: Response, db: Annotated[Session, Depends(get_db)]):
    """Cierra la sesión: revoca el token y borra la cookie."""
    token = extraer_token(request)
    payload = decodificar_token(token) if token else None
    if payload:
        tokens_revocados.revocar(payload.get("jti"), payload.get("exp"))
        audit.registrar(db, "logout", int(payload["sub"]), "Usuario", payload["sub"],
                        "Cierre de sesión", ip=_ip(request))
    response.delete_cookie(COOKIE_NAME, path="/", secure=settings.COOKIE_SECURE,
                           httponly=True, samesite="strict")


@router.get("/me")
def me(usuario: CurrentUser):
    return {
        "id": usuario.id,
        "nombre": usuario.nombre,
        "email": usuario.email,
        "rol": usuario.rol.nombre,
        "permisos": usuario.rol.permisos,
    }
