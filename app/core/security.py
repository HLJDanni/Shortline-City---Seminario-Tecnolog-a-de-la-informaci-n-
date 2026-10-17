"""Utilidades de seguridad: hash de contraseñas, JWT y control de intentos.

Cumple RNF-001 (hash seguro, nunca texto plano), RF-055/RF-060 (sesiones/JWT)
y RNF-002/RNF-003 (protección del acceso).
"""
import secrets
import threading
import time
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

TOKEN_ISSUER = "shoreline-city"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# ------------------------------------------------------------------- JWT
def crear_token(sub: str, extra: dict | None = None) -> str:
    """Genera un JWT firmado con expiración, emisor e identificador único (RF-060)."""
    ahora = datetime.now(timezone.utc)
    payload = {
        "sub": str(sub),
        "iat": ahora,
        "exp": ahora + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        "iss": TOKEN_ISSUER,
        "jti": secrets.token_urlsafe(16),
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decodificar_token(token: str) -> dict | None:
    """Valida firma, algoritmo, expiración y emisor. Rechaza tokens revocados."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],   # nunca acepta "none" ni otro algoritmo
            issuer=TOKEN_ISSUER,
        )
    except JWTError:
        return None
    if tokens_revocados.contiene(payload.get("jti")):
        return None
    return payload


class _ListaRevocacion:
    """Tokens cerrados con logout antes de su expiración (en memoria)."""

    def __init__(self) -> None:
        self._jtis: dict[str, float] = {}
        self._lock = threading.Lock()

    def revocar(self, jti: str | None, exp: float | int | None) -> None:
        if not jti:
            return
        with self._lock:
            self._jtis[jti] = float(exp or time.time() + 86400)
            ahora = time.time()
            self._jtis = {j: e for j, e in self._jtis.items() if e > ahora}

    def contiene(self, jti: str | None) -> bool:
        if not jti:
            return False
        with self._lock:
            exp = self._jtis.get(jti)
            return exp is not None and exp > time.time()

    def limpiar(self) -> None:
        with self._lock:
            self._jtis.clear()


tokens_revocados = _ListaRevocacion()


# ------------------------------------------------- Intentos de login
class ControlIntentos:
    """Bloquea temporalmente un correo o IP tras varios intentos fallidos."""

    def __init__(self) -> None:
        self._fallos: dict[str, list[float]] = {}
        self._lock = threading.Lock()

    @property
    def _ventana(self) -> float:
        return settings.LOGIN_BLOQUEO_MINUTOS * 60

    def _recientes(self, clave: str, ahora: float) -> list[float]:
        return [t for t in self._fallos.get(clave, []) if ahora - t < self._ventana]

    def bloqueado(self, *claves: str) -> int:
        """Segundos restantes de bloqueo (0 si no está bloqueado)."""
        ahora = time.time()
        with self._lock:
            restante = 0
            for clave in claves:
                fallos = self._recientes(clave, ahora)
                if len(fallos) >= settings.LOGIN_MAX_INTENTOS:
                    restante = max(restante, int(self._ventana - (ahora - fallos[0])) + 1)
            return restante

    def fallo(self, *claves: str) -> None:
        ahora = time.time()
        with self._lock:
            for clave in claves:
                self._fallos[clave] = self._recientes(clave, ahora) + [ahora]

    def exito(self, *claves: str) -> None:
        with self._lock:
            for clave in claves:
                self._fallos.pop(clave, None)

    def limpiar(self) -> None:
        with self._lock:
            self._fallos.clear()


control_intentos = ControlIntentos()
