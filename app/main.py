"""Punto de entrada de la aplicación FastAPI - Shoreline City.

Sistema centralizado para la gestión de información de las personas
relacionadas con la Iglesia Shoreline City.

Backend API REST + SPA en Vue 3 (servido como archivos estáticos compilados).
"""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.core.deps import CredentialsError
from app.routers import auth, operacion, personas
from app.seed import sembrar

# Importa todos los modelos para registrar el metadata.
import app.models  # noqa: F401

BASE_DIR = Path(__file__).resolve().parent.parent
# El build de Vue se copia aquí en la imagen Docker; en local: frontend/dist.
for _candidato in (BASE_DIR / "frontend_dist", BASE_DIR / "frontend" / "dist"):
    if _candidato.exists():
        FRONTEND_DIST = _candidato
        break
else:
    FRONTEND_DIST = BASE_DIR / "frontend_dist"


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        sembrar(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="Sistema centralizado de gestión de información - Iglesia Shoreline City",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS: permite el servidor de desarrollo de Vite (npm run dev).
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------- HTTPS y cabeceras de seguridad (RNF-002) -------------------
_CSP = (
    "default-src 'self'; "
    "script-src 'self'; "
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
    "font-src 'self' data: https://fonts.gstatic.com; "
    "img-src 'self' data: blob:; "
    "connect-src 'self'; "
    "frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
)
_SIN_CSP = ("/docs", "/redoc", "/openapi.json")  # Swagger carga recursos de un CDN


@app.middleware("http")
async def seguridad_http(request: Request, call_next):
    # En producción todo el tráfico debe ser HTTPS. Render termina TLS y avisa
    # con X-Forwarded-Proto (uvicorn --proxy-headers lo refleja en el esquema).
    if (settings.es_produccion and request.url.scheme == "http"
            and request.url.path != "/health"):
        return RedirectResponse(str(request.url.replace(scheme="https")), status_code=308)

    response = await call_next(request)
    h = response.headers
    h.setdefault("X-Content-Type-Options", "nosniff")
    h.setdefault("X-Frame-Options", "DENY")
    h.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    h.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    if not request.url.path.startswith(_SIN_CSP):
        h.setdefault("Content-Security-Policy", _CSP)
    if request.url.path.startswith("/api/"):
        h.setdefault("Cache-Control", "no-store")
    if settings.es_produccion:
        h.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
    return response


@app.exception_handler(CredentialsError)
async def credenciales_handler(request: Request, exc: CredentialsError):
    return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)


@app.get("/health", tags=["sistema"])
def health():
    return {"status": "ok", "app": settings.APP_NAME}


# --------------------------- API REST (RF-065) ---------------------------
app.include_router(auth.router)
app.include_router(personas.router)
app.include_router(operacion.router)


# ----------------------- SPA (Vue 3 compilado) --------------------------
if (FRONTEND_DIST / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")


@app.get("/{full_path:path}", include_in_schema=False)
async def servir_spa(full_path: str):
    """Entrega el SPA. Las rutas de Vue Router se resuelven en el cliente."""
    if full_path.startswith(("api", "docs", "openapi.json", "redoc", "health")):
        return JSONResponse({"detail": "No encontrado"}, status_code=404)
    index = FRONTEND_DIST / "index.html"
    if index.exists():
        return FileResponse(str(index))
    return JSONResponse(
        {"detail": "Frontend no compilado. Ejecute el build de Vue "
                   "(docker compose build) o 'npm run dev' en frontend/."},
        status_code=503,
    )
