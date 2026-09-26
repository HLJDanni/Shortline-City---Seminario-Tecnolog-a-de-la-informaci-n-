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
