# Guía de despliegue

## Requisitos

- Docker y Docker Compose
- (Producción) dominio con certificado TLS y un proxy inverso
  (Nginx / Traefik / Caddy) delante de la app

## 1. Configuración

```bash
cp .env.example .env
```

Edite `.env`:

- `SECRET_KEY`: genere una con `openssl rand -hex 32`.
- `POSTGRES_PASSWORD`: contraseña robusta.
- `FIRST_ADMIN_EMAIL` / `FIRST_ADMIN_PASSWORD`: credenciales del admin inicial.
- En producción con HTTPS: `COOKIE_SECURE=true` y `ENVIRONMENT=production`.

## 2. Levantar los servicios

```bash
docker compose up --build -d
docker compose logs -f web        # ver el arranque
```

La app crea las tablas y siembra roles + admin automáticamente al iniciar.

- App: `http://localhost:8080`
- Swagger: `http://localhost:8080/docs`
- Health: `http://localhost:8080/health`

## 3. HTTPS/TLS en producción (RNF-002)

Coloque un proxy inverso que termine TLS y reenvíe a `web:8000`. Ejemplo
mínimo con Nginx:

```nginx
server {
    listen 443 ssl;
    server_name shoreline.midominio.org;
    ssl_certificate     /etc/ssl/cert.pem;
    ssl_certificate_key /etc/ssl/key.pem;
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 4. Respaldos (RF-061 / RF-062, RNF-011)

Programe un cron diario en el host:

```cron
0 2 * * * cd /ruta/shoreline_city && ./scripts/backup.sh
```

Prueba de restauración periódica:

```bash
./scripts/restore.sh scripts/backup/shoreline_YYYYMMDD_HHMMSS.dump
```

## 5. Actualizaciones

```bash
git pull
docker compose up --build -d
```

Las migraciones simples se aplican con `create_all` (nuevas tablas). Para
cambios de esquema complejos se recomienda integrar Alembic en el futuro.

## 6. Verificación post-despliegue

```bash
curl -s http://localhost:8080/health          # {"status":"ok"}
docker compose exec web python -m pytest -q    # opcional
```

---

# Despliegue en la nube: Render + Supabase

Alternativa sin servidor propio: **Supabase** aloja PostgreSQL y **Render**
ejecuta el mismo `Dockerfile` (API + SPA). Render entrega HTTPS, por lo que
no se necesita Nginx.

## 1. Supabase

1. Crear el proyecto (región cercana a la de Render, p. ej. us-east-1).
2. En **Connect**, copiar la cadena del **Session pooler** (puerto 5432):
   `postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:5432/postgres`
   - No usar la conexión directa `db.[ref].supabase.co`: es IPv6 y Render
     solo sale por IPv4.
   - La app adapta sola el prefijo a `postgresql+psycopg://` y agrega
     `sslmode=require` (`app/core/config.py`).

## 2. Render (Web Service, runtime Docker)

| Variable | Valor |
|----------|-------|
| `DATABASE_URL` | Cadena del Session pooler con la contraseña real |
| `SECRET_KEY` | `openssl rand -hex 32` |
| `ENVIRONMENT` | `production` |
| `COOKIE_SECURE` | `true` |
| `FIRST_ADMIN_EMAIL` / `FIRST_ADMIN_PASSWORD` / `FIRST_ADMIN_NAME` | Admin inicial |

- Health Check Path: `/health`. El puerto lo fija Render con `PORT`.
- Al arrancar, la app crea las tablas en Supabase y siembra roles y admin.

## 3. Después del primer despliegue

- Ejecutar `scripts/supabase_rls.sql` en Supabase > SQL Editor (bloquea la
  Data API pública).
- Datos demo desde un equipo local:
  `DATABASE_URL="<cadena pooler>" python -m scripts.seed_demo`
- Respaldos: `DATABASE_URL="<cadena pooler>" ./scripts/backup.sh`

## 4. Seguridad de la sesión (HTTPS + JWT)

| Medida | Implementación |
|--------|----------------|
| HTTPS obligatorio | Render entrega TLS; en producción la app redirige HTTP→HTTPS (308) y envía `Strict-Transport-Security` |
| JWT en cookie | `HttpOnly` (JS no lo lee), `Secure` (solo HTTPS), `SameSite=Strict` (sin envío desde otros sitios) |
| JWT validado | Firma HS256 fija, expiración, emisor (`iss`) e id único (`jti`); se revoca al cerrar sesión |
| Fuerza bruta | 5 intentos fallidos por correo o IP → bloqueo de 15 min (HTTP 429) |
| Enumeración de usuarios | Mismo tiempo de respuesta exista o no el correo |
| Cabeceras | CSP, `X-Frame-Options: DENY`, `nosniff`, `Referrer-Policy`, `Cache-Control: no-store` en `/api` |
| Arranque seguro | En `ENVIRONMENT=production` la app no inicia con `SECRET_KEY` débil ni con la contraseña de admin por defecto |

Integraciones externas (RF-065) siguen usando `Authorization: Bearer <token>`
con el token que devuelve `POST /api/auth/login`.
