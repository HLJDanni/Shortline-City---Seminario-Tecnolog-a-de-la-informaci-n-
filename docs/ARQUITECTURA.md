# Arquitectura

## Visión general

Aplicación web monolítica modular en capas, contenerizada con Docker. Una
**base de datos central** relacional garantiza que una persona mantenga el
mismo `id` en todos los módulos (RF-069).

```
Navegador (PC / tablet / móvil)
        │  HTTPS
        ▼
┌─────────────────────────────────────────────┐
│  FastAPI (app.main)                          │
│  ┌───────────────┐   ┌────────────────────┐  │
│  │ Vistas Jinja2 │   │ API REST (/api/...) │  │
│  │  (app/web)    │   │  (app/routers)      │  │
│  └───────┬───────┘   └─────────┬──────────┘  │
│          ▼ seguridad/RBAC ▼ (app/core/deps)  │
│  ┌─────────────────────────────────────────┐ │
│  │ Servicios / lógica de negocio           │ │
│  │ (app/services)                          │ │
│  └───────────────────┬─────────────────────┘ │
│                      ▼ ORM (SQLAlchemy)       │
└──────────────────────┼────────────────────────┘
                       ▼
              PostgreSQL 18 (Docker)
```

## Capas (según hoja *Arquitectura* del Excel)

| Capa | Implementación |
|------|----------------|
| Frontend | Vistas Jinja2 responsive (`app/web`, `app/templates`) — PWA-ready |
| Backend | FastAPI: autenticación, validaciones, reglas, auditoría |
| Base de datos | PostgreSQL 18 relacional (`app/models`) |
| Integraciones | API REST + preparación para Webhooks/n8n (RF-065 a RF-068) |
| Seguridad | HTTPS/TLS (producción), RBAC, JWT, sesiones, backups |
| Observabilidad | Auditoría + `/health` + logs |

## Decisiones de diseño

- **Separación API / vistas**: la misma lógica de negocio (`app/services`)
  alimenta tanto la API REST como el frontend, evitando duplicación (RNF-008).
- **Autenticación dual**: JWT en cookie HttpOnly para el navegador y
  `Authorization: Bearer` para integraciones/API (RF-065).
- **RBAC por `modulo:accion`**: dependencia `require_permission()` aplicada
  en cada endpoint (RF-057, RNF-003).
- **Baja lógica** de personas (`activo=False`) para preservar integridad
  referencial e historial.
- **Tipos genéricos + JSON** en el ORM: compatibilidad PostgreSQL/SQLite,
  lo que permite pruebas rápidas sin servicios externos (RNF-009).
- **Auditoría e historial** desacoplados en `services/auditoria_service.py`
  (RF-058, RF-009).

## Escalabilidad (RNF-005)

El modelo por módulos y la configuración por catálogos (RF-070) permiten
crecer en personas, servicios y formularios sin rediseño. El backend es
sin estado (stateless salvo la sesión JWT), por lo que puede escalarse
horizontalmente detrás de un balanceador.
