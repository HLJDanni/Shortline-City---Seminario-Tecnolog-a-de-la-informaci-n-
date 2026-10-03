# Shoreline City — Sistema Centralizado de Gestión de Personas

Sistema web para centralizar la gestión de información de las personas
relacionadas con la **Iglesia Shoreline City**: personas, servicios,
check-in de asistencia, gafetes (Name Tags), proceso *Únete*, conteos de
ushers, voluntariado, formularios, analíticas, seguridad y auditoría.

> Trabajo de graduación — Facultad de Ingeniería en Sistemas, Universidad
> Mariano Gálvez de Guatemala (UMG).

## Stack tecnológico

| Capa | Tecnología |
|------|-----------|
| Backend / API | **Python 3.12 + FastAPI** |
| Base de datos | **PostgreSQL 18** (SQLAlchemy 2.0 ORM) |
| Frontend | **Vue 3 + Vite + Vuetify 3** (SPA, Material Design, responsive) |
| Estado / rutas | Pinia + Vue Router |
| Seguridad | JWT (Bearer), bcrypt, RBAC por permisos |
| Contenedores | **Docker + Docker Compose** (build multi-stage) |
| Pruebas | pytest (unitarias, integración y funcionales) |

El frontend es una **SPA en Vue 3** que consume la API REST de FastAPI. En
producción, Vite compila el SPA y FastAPI lo sirve como archivos estáticos
(todo dentro de la imagen Docker mediante un build multi-stage; no necesitas
instalar Node en tu equipo).

## Arranque rápido con Docker

```bash
cp .env.example .env          # ajuste SECRET_KEY y credenciales
docker compose up --build     # levanta PostgreSQL 18 + la app
```

Luego abra **http://localhost:8080**

- Usuario inicial: `admin@shorelinecity.org`
- Contraseña: `Admin1234` (definida en `.env`, cámbiela)

Documentación interactiva de la API (Swagger): **http://localhost:8080/docs**

### Cargar datos de demostración (opcional)

```bash
docker compose exec web python -m scripts.seed_demo
```

Crea 12 personas, 3 servicios con check-ins y una cohorte de *Únete*.

## Desarrollo local (sin Docker)

**Backend:**
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL="sqlite:///./shoreline.db"   # o apunte a su PostgreSQL
uvicorn app.main:app --reload --port 8080
```

**Frontend (con recarga en caliente):**
```bash
cd frontend
npm install
npm run dev        # http://localhost:5173  (proxy /api -> :8080)
```

Para producción/local integrado, compile el SPA y déjelo listo para FastAPI:
```bash
cd frontend && npm run build   # genera frontend/dist, que FastAPI sirve
```

## Pruebas

```bash
pip install -r requirements.txt
python -m pytest -q
```

Las pruebas corren sobre SQLite (no requieren PostgreSQL). Cubren
autenticación, RBAC, personas, control de duplicados, check-in, conteos,
analíticas y las vistas web. **27 pruebas, todas en verde.**

## Estructura del proyecto

```
shoreline_city/
├── app/                    # Backend (FastAPI)
│   ├── main.py             # Entrada: API + sirve el SPA compilado
│   ├── seed.py             # Roles, admin y catálogos iniciales
│   ├── core/               # config, database, security, deps (RBAC)
│   ├── models/             # Modelos SQLAlchemy (entidades)
│   ├── schemas/            # Esquemas Pydantic (validación)
│   ├── services/           # Lógica de negocio
│   └── routers/            # API REST (/api/...)
├── frontend/               # SPA (Vue 3 + Vite + Vuetify)
│   ├── src/
│   │   ├── views/          # Login, Dashboard, Personas, Check-in, ...
│   │   ├── layouts/        # Layout principal (drawer + app bar)
│   │   ├── stores/         # Pinia (auth)
│   │   ├── router.js       # Vue Router + guardas
│   │   └── api.js          # Cliente axios (token JWT)
│   └── package.json
├── tests/                  # Pruebas automatizadas
├── scripts/                # backup.sh, restore.sh, seed_demo.py
├── docs/                   # Arquitectura, modelo de datos, trazabilidad
├── docker-compose.yml      # PostgreSQL 18 + web
├── Dockerfile
└── requirements.txt
```

## Roles y permisos (RBAC)

Seis roles predefinidos (hoja *Roles y permisos* del Excel):
Administrador, Coordinador, Líder, Usher, Operador y Administrador técnico.
Los permisos se controlan por `modulo:accion`
(`ver`, `crear`, `editar`, `eliminar`, `exportar`) según RF-057 y el
principio de mínimo privilegio (RNF-003).

## Respaldos (RF-061 / RF-062)

```bash
./scripts/backup.sh                              # crea un dump con retención
./scripts/restore.sh scripts/backup/archivo.dump # restaura
```

## Documentación adicional

- [`docs/ARQUITECTURA.md`](docs/ARQUITECTURA.md)
- [`docs/MODELO_DATOS.md`](docs/MODELO_DATOS.md)
- [`docs/DESPLIEGUE.md`](docs/DESPLIEGUE.md)
- [`docs/TRAZABILIDAD.md`](docs/TRAZABILIDAD.md) — matriz requerimiento → implementación

## Alcance de esta entrega

Cubre el **MVP** completo (Personas, autenticación/roles, servicios,
Check-in, Name Tags, Únete, conteos y dashboard) más auditoría, API REST y
la base de Formularios/Voluntariado. Las fases 2–4 (formularios avanzados,
n8n, mensajería, contingencia offline, app móvil, IA) están previstas en la
arquitectura sin necesidad de rediseño (RNF-005).
