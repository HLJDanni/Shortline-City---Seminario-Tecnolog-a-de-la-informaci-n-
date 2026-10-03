# Modelo de datos

Basado en la hoja *Datos principales* del documento de requerimientos.
Todas las entidades comparten la persona como eje central (RF-069).

## Entidades principales

| Tabla | Descripción | Requerimientos |
|-------|-------------|----------------|
| `personas` | Núcleo: datos personales, estado, campos extra | RF-001–010 |
| `familias` | Agrupación familiar | RF-007 |
| `etiquetas` / `persona_etiqueta` | Segmentación N:M | RF-008 |
| `historial_persona` | Historial de cambios/eventos | RF-009 |
| `usuarios` | Cuentas de acceso | RF-055 |
| `roles` | Roles y lista de permisos (JSON) | RF-056/057 |
| `servicios` | Servicios y eventos especiales | RF-011, RF-034/035 |
| `checkins` | Registro de asistencia | RF-012–016 |
| `plantillas_nametag` / `nametags` | Gafetes | RF-017–020 |
| `cohortes` | Ediciones de *Únete* | RF-021 |
| `inscripciones_unete` | Persona ↔ cohorte + estado | RF-022/024 |
| `sesiones_unete` / `asistencia_unete` | Sesiones y asistencia | RF-025 |
| `eventos_unete` | Línea de tiempo | RF-028 |
| `categorias_conteo` / `conteos` / `conteo_detalle` | Conteos ushers | RF-029–033 |
| `equipos` / `roles_equipo` / `asignaciones` | Voluntariado | RF-051–054 |
| `formularios` / `campos_formulario` / `respuestas_formulario` | Formularios dinámicos | RF-043–050 |
| `auditoria` | Registro de actividad | RF-058 |

## Relaciones clave

```
persona 1───N checkin N───1 servicio
persona 1───N inscripcion_unete N───1 cohorte 1───N sesion_unete
inscripcion_unete 1───N asistencia_unete N───1 sesion_unete
inscripcion_unete 1───N evento_unete            (línea de tiempo)
servicio 1───N conteo 1───N conteo_detalle N───1 categoria_conteo
persona 1───N asignacion N───1 equipo 1───N rol_equipo
formulario 1───N campo_formulario
formulario 1───N respuesta_formulario N───0..1 persona
usuario N───1 rol
persona 1───N historial_persona
```

## Estados (catálogos)

- **Persona**: nuevo, activo, inactivo, visitante, miembro
- **Servicio**: programado, en_curso, finalizado, cancelado
- **Check-in**: registrado, anulado
- **Cohorte**: abierta, en_curso, finalizada, cancelada
- **Inscripción Únete**: inscrito, en_proceso, completado, integrado, retirado
  (habilita el embudo del dashboard, RF-040)
- **Formulario**: borrador, publicado, cerrado

Los catálogos de categorías de conteo, etiquetas y roles son configurables
desde datos, sin modificar código (RF-070).
