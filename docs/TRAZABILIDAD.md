# Matriz de trazabilidad de requerimientos

Estado: **✅ Implementado** · **🟡 Base/parcial** (estructura lista, ampliable) ·
**⏳ Fase futura** (previsto en arquitectura).

## Requerimientos funcionales

| ID | Nombre | Estado | Dónde |
|----|--------|--------|-------|
| RF-001 | Crear persona (ID único) | ✅ | `persona_service.crear_persona`, `routers/personas` |
| RF-002 | Editar persona | ✅ | `persona_service.actualizar_persona` |
| RF-003 | Buscar persona | ✅ | `persona_service.buscar` |
| RF-004 | Filtros avanzados | ✅ | `buscar` (estado, etiqueta, combinables) |
| RF-005 | Perfil 360° | ✅ | `templates/persona_detalle.html` |
| RF-006 | Control de duplicados | ✅ | `detectar_duplicados` + 409/forzar |
| RF-007 | Familias | 🟡 | modelo `Familia` |
| RF-008 | Etiquetas | 🟡 | modelo `Etiqueta` + N:M |
| RF-009 | Historial | ✅ | `historial_persona`, `auditoria_service` |
| RF-010 | Importación CSV/Excel | ⏳ | openpyxl disponible; endpoint pendiente |
| RF-011 | Configurar servicios | ✅ | `routers/operacion`, `templates/servicios` |
| RF-012 | Registrar asistencia | ✅ | `checkin_service.registrar_checkin` |
| RF-013 | Check-in rápido | ✅ | `templates/checkin.html` |
| RF-014 | Persona nueva desde Check-in | ✅ | enlace a alta desde check-in |
| RF-015 | Historial de asistencia | ✅ | perfil de persona / API |
| RF-016 | Corrección de asistencia | ✅ | `anular_checkin` con auditoría |
| RF-017 | Diseño de Name Tag | ✅ | `PlantillaNameTag`, `templates/nametag` |
| RF-018 | Impresión | ✅ | impresión por navegador |
| RF-019 | Impresora Bluetooth | ⏳ | punto de integración documentado |
| RF-020 | Reimpresión | 🟡 | campo `reimpresion` en modelo |
| RF-021 | Crear cohorte/clase | ✅ | modelo `Cohorte`, vista Únete |
| RF-022 | Inscripción | ✅ | `InscripcionUnete` |
| RF-023 | Lista de seguimiento | ✅ | vista Únete (tabla) |
| RF-024 | Estados | ✅ | `EstadoInscripcion` |
| RF-025 | Asistencia por sesión | 🟡 | `SesionUnete`, `AsistenciaUnete` |
| RF-026 | Responsable | 🟡 | campo `responsable_id` |
| RF-027 | Notas | 🟡 | campo `notas` |
| RF-028 | Línea de tiempo | 🟡 | `EventoUnete` |
| RF-029 | Conteo rápido | ✅ | `templates/conteos.html` (+/−) |
| RF-030 | Categorías | ✅ | `CategoriaConteo` configurable |
| RF-031 | Total automático | ✅ | `Conteo.recalcular_total` (test) |
| RF-032 | Responsable del conteo | ✅ | `responsable_id`, fecha/hora |
| RF-033 | Corrección de conteo | 🟡 | campos `valor_anterior`, `motivo` |
| RF-034 | Calendario de servicios | ✅ | vista servicios |
| RF-035 | Servicios especiales | ✅ | campo `especial` |
| RF-036 | Dashboard general | ✅ | `analitica_service.kpis_generales` |
| RF-037 | Asistencia mensual | 🟡 | base analítica |
| RF-038 | Asistencia por servicio | ✅ | `asistencia_por_servicio` |
| RF-039 | Personas nuevas | ✅ | KPI 30 días |
| RF-040 | Embudo de Únete | ✅ | `embudo_unete` |
| RF-041 | Voluntariado | 🟡 | modelos de equipos |
| RF-042 | Exportar reportes | ⏳ | openpyxl disponible |
| RF-043–050 | Formularios dinámicos | 🟡 | modelos completos, UI en Fase 2 |
| RF-051 | Equipos | 🟡 | `Equipo` |
| RF-052 | Roles de equipo | 🟡 | `RolEquipo` |
| RF-053 | Asignaciones | 🟡 | `Asignacion` |
| RF-054 | Disponibilidad | 🟡 | campo `disponibilidad` |
| RF-055 | Autenticación | ✅ | `routers/auth`, JWT |
| RF-056 | Roles | ✅ | `seed.ROLES_BASE`, modelo `Rol` |
| RF-057 | Permisos | ✅ | `require_permission` (test RBAC) |
| RF-058 | Registro de actividad | ✅ | `auditoria_service.registrar` |
| RF-059 | Validación de entradas | ✅ | esquemas Pydantic |
| RF-060 | Sesiones | ✅ | expiración JWT, logout |
| RF-061 | Respaldo | ✅ | `scripts/backup.sh` |
| RF-062 | Restauración | ✅ | `scripts/restore.sh` |
| RF-063 | Responsive | ✅ | Bootstrap 5, meta viewport |
| RF-064 | Check-in offline | ⏳ | Fase 3 |
| RF-065 | API REST | ✅ | `/api/*` + `/docs` |
| RF-066–068 | Webhooks / n8n / Mensajería | ⏳ | Fase 3 (API base lista) |
| RF-069 | Base de datos central | ✅ | ID único de persona compartido |
| RF-070 | Configuración por catálogos | ✅ | categorías/roles/etiquetas en datos |

## Requerimientos no funcionales

| ID | Categoría | Estado | Dónde |
|----|-----------|--------|-------|
| RNF-001 | Hash de contraseñas | ✅ | bcrypt (`core/security`), test |
| RNF-002 | HTTPS/TLS | ✅ | guía de despliegue + `COOKIE_SECURE` |
| RNF-003 | Mínimo privilegio | ✅ | RBAC por permiso |
| RNF-004 | Rendimiento búsquedas | ✅ | índices en nombres/teléfono/correo |
| RNF-005 | Escalabilidad | ✅ | backend stateless, modular |
| RNF-006 | Disponibilidad | 🟡 | healthcheck + docs |
| RNF-007 | Usabilidad check-in/conteos | ✅ | vistas de pocos pasos |
| RNF-008 | Mantenibilidad | ✅ | código modular y documentado |
| RNF-009 | Pruebas | ✅ | 27 pruebas (unit/integración/funcional) |
| RNF-010 | Privacidad | ✅ | RBAC + baja lógica |
| RNF-011 | Backups | ✅ | scripts con retención |
| RNF-012 | Observabilidad | ✅ | auditoría + `/health` |
| RNF-013 | Compatibilidad | 🟡 | navegadores modernos (Bootstrap 5) |
| RNF-014 | Accesibilidad | 🟡 | labels y contraste base |
| RNF-015 | Documentación | ✅ | `README` + `docs/` |
