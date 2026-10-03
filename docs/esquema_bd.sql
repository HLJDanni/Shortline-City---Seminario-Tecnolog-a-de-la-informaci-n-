-- ============================================================================
--  Shoreline City — Esquema de base de datos (PostgreSQL 18)
--  Sistema centralizado de gestión de información de personas
--  Universidad Mariano Gálvez de Guatemala — Seminario / Graduación
-- ============================================================================
--  Nota: en la aplicación las tablas se crean automáticamente vía SQLAlchemy
--  (Base.metadata.create_all). Este archivo documenta ese esquema y permite
--  recrearlo manualmente. Incluye DEFAULT a nivel de base para las columnas
--  cuyo valor por defecto normalmente lo asigna el ORM.
-- ============================================================================

-- ------------------------- Seguridad / Usuarios -----------------------------
CREATE TABLE roles (
    id          SERIAL PRIMARY KEY,
    nombre      VARCHAR(60)  NOT NULL UNIQUE,
    descripcion VARCHAR(255) NOT NULL DEFAULT '',
    permisos    JSON         NOT NULL DEFAULT '[]',   -- ["modulo:accion", ...] o ["*"]
    sistema     BOOLEAN      NOT NULL DEFAULT FALSE
);

CREATE TABLE usuarios (
    id              SERIAL PRIMARY KEY,
    nombre          VARCHAR(120) NOT NULL,
    email           VARCHAR(160) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,            -- bcrypt (nunca texto plano)
    activo          BOOLEAN      NOT NULL DEFAULT TRUE,
    rol_id          INTEGER      NOT NULL REFERENCES roles(id),
    creado_en       TIMESTAMP    NOT NULL DEFAULT now(),
    ultimo_acceso   TIMESTAMP
);
CREATE INDEX ix_usuarios_email ON usuarios(email);

-- ------------------------------ Personas ------------------------------------
CREATE TABLE familias (
    id        SERIAL PRIMARY KEY,
    nombre    VARCHAR(120) NOT NULL,
    creada_en TIMESTAMP    NOT NULL DEFAULT now()
);

CREATE TABLE etiquetas (
    id     SERIAL PRIMARY KEY,
    nombre VARCHAR(60) NOT NULL UNIQUE,
    color  VARCHAR(20) NOT NULL DEFAULT '#0d6efd'
);

CREATE TABLE personas (
    id               SERIAL PRIMARY KEY,
    nombres          VARCHAR(120) NOT NULL,
    apellidos        VARCHAR(120) NOT NULL DEFAULT '',
    telefono         VARCHAR(30),
    correo           VARCHAR(160),
    direccion        VARCHAR(255),
    fecha_nacimiento DATE,
    genero           VARCHAR(20),
    estado           VARCHAR(20)  NOT NULL DEFAULT 'nuevo',
    notas            VARCHAR(1000),
    campos_extra     JSON         NOT NULL DEFAULT '{}',
    activo           BOOLEAN      NOT NULL DEFAULT TRUE,
    familia_id       INTEGER      REFERENCES familias(id),
    creada_en        TIMESTAMP    NOT NULL DEFAULT now(),
    actualizada_en   TIMESTAMP    NOT NULL DEFAULT now()
);
CREATE INDEX ix_personas_nombres   ON personas(nombres);
CREATE INDEX ix_personas_apellidos ON personas(apellidos);
CREATE INDEX ix_personas_telefono  ON personas(telefono);
CREATE INDEX ix_personas_correo    ON personas(correo);

-- Relación N:M personas <-> etiquetas
CREATE TABLE persona_etiqueta (
    persona_id  INTEGER NOT NULL REFERENCES personas(id)  ON DELETE CASCADE,
    etiqueta_id INTEGER NOT NULL REFERENCES etiquetas(id) ON DELETE CASCADE,
    PRIMARY KEY (persona_id, etiqueta_id)
);

CREATE TABLE historial_persona (
    id         SERIAL PRIMARY KEY,
    persona_id INTEGER NOT NULL REFERENCES personas(id) ON DELETE CASCADE,
    usuario_id INTEGER REFERENCES usuarios(id),
    accion     VARCHAR(80)  NOT NULL,
    detalle    VARCHAR(500) NOT NULL DEFAULT '',
    fecha      TIMESTAMP    NOT NULL DEFAULT now()
);

-- ------------------------- Servicios / Check-in -----------------------------
CREATE TABLE servicios (
    id        SERIAL PRIMARY KEY,
    nombre    VARCHAR(120) NOT NULL,
    fecha     DATE         NOT NULL,
    hora      TIME,
    ubicacion VARCHAR(160),
    tipo      VARCHAR(60)  NOT NULL DEFAULT 'regular',
    especial  BOOLEAN      NOT NULL DEFAULT FALSE,
    estado    VARCHAR(20)  NOT NULL DEFAULT 'programado',
    creado_en TIMESTAMP    NOT NULL DEFAULT now()
);
CREATE INDEX ix_servicios_fecha ON servicios(fecha);

CREATE TABLE checkins (
    id                 SERIAL PRIMARY KEY,
    persona_id         INTEGER NOT NULL REFERENCES personas(id),
    servicio_id        INTEGER NOT NULL REFERENCES servicios(id),
    operador_id        INTEGER REFERENCES usuarios(id),
    fecha_hora         TIMESTAMP   NOT NULL DEFAULT now(),
    estado             VARCHAR(20) NOT NULL DEFAULT 'registrado',
    motivo_correccion  VARCHAR(255)
);

CREATE TABLE plantillas_nametag (
    id     SERIAL PRIMARY KEY,
    nombre VARCHAR(80) NOT NULL,
    campos JSON        NOT NULL DEFAULT '["nombre","fecha"]',
    activa BOOLEAN     NOT NULL DEFAULT TRUE
);

CREATE TABLE nametags (
    id          SERIAL PRIMARY KEY,
    persona_id  INTEGER NOT NULL REFERENCES personas(id),
    plantilla_id INTEGER NOT NULL REFERENCES plantillas_nametag(id),
    servicio_id INTEGER REFERENCES servicios(id),
    impresora   VARCHAR(120),
    reimpresion BOOLEAN   NOT NULL DEFAULT FALSE,
    fecha       TIMESTAMP NOT NULL DEFAULT now()
);

-- ------------------------------ Conteos -------------------------------------
CREATE TABLE categorias_conteo (
    id     SERIAL PRIMARY KEY,
    nombre VARCHAR(60) NOT NULL UNIQUE,
    activa BOOLEAN     NOT NULL DEFAULT TRUE
);

CREATE TABLE conteos (
    id             SERIAL PRIMARY KEY,
    servicio_id    INTEGER NOT NULL REFERENCES servicios(id),
    responsable_id INTEGER REFERENCES usuarios(id),
    fecha_hora     TIMESTAMP NOT NULL DEFAULT now(),
    total          INTEGER   NOT NULL DEFAULT 0
);

CREATE TABLE conteo_detalle (
    id                SERIAL PRIMARY KEY,
    conteo_id         INTEGER NOT NULL REFERENCES conteos(id) ON DELETE CASCADE,
    categoria_id      INTEGER NOT NULL REFERENCES categorias_conteo(id),
    cantidad          INTEGER NOT NULL DEFAULT 0,
    valor_anterior    INTEGER,                 -- auditoría de corrección (RF-033)
    motivo_correccion VARCHAR(255)
);

-- -------------------------------- Únete -------------------------------------
CREATE TABLE cohortes (
    id             SERIAL PRIMARY KEY,
    nombre         VARCHAR(120) NOT NULL,
    fecha_inicio   DATE,
    horario        VARCHAR(120),
    ubicacion      VARCHAR(160),
    responsable_id INTEGER REFERENCES usuarios(id),
    estado         VARCHAR(20) NOT NULL DEFAULT 'abierta',
    creada_en      TIMESTAMP   NOT NULL DEFAULT now()
);

CREATE TABLE inscripciones_unete (
    id             SERIAL PRIMARY KEY,
    persona_id     INTEGER NOT NULL REFERENCES personas(id),
    cohorte_id     INTEGER NOT NULL REFERENCES cohortes(id) ON DELETE CASCADE,
    estado         VARCHAR(20) NOT NULL DEFAULT 'inscrito',
    responsable_id INTEGER REFERENCES usuarios(id),
    notas          VARCHAR(1000),
    creada_en      TIMESTAMP   NOT NULL DEFAULT now()
);

CREATE TABLE sesiones_unete (
    id         SERIAL PRIMARY KEY,
    cohorte_id INTEGER NOT NULL REFERENCES cohortes(id) ON DELETE CASCADE,
    numero     INTEGER NOT NULL DEFAULT 1,
    nombre     VARCHAR(120),
    fecha      DATE
);

CREATE TABLE asistencia_unete (
    id             SERIAL PRIMARY KEY,
    inscripcion_id INTEGER NOT NULL REFERENCES inscripciones_unete(id) ON DELETE CASCADE,
    sesion_id      INTEGER NOT NULL REFERENCES sesiones_unete(id)      ON DELETE CASCADE,
    asistio        BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE eventos_unete (               -- línea de tiempo (RF-028)
    id             SERIAL PRIMARY KEY,
    inscripcion_id INTEGER NOT NULL REFERENCES inscripciones_unete(id) ON DELETE CASCADE,
    tipo           VARCHAR(60)  NOT NULL,
    detalle        VARCHAR(500) NOT NULL DEFAULT '',
    fecha          TIMESTAMP    NOT NULL DEFAULT now()
);

-- ----------------------------- Voluntariado ---------------------------------
CREATE TABLE equipos (
    id     SERIAL PRIMARY KEY,
    nombre VARCHAR(120) NOT NULL UNIQUE,
    activo BOOLEAN      NOT NULL DEFAULT TRUE
);

CREATE TABLE roles_equipo (
    id        SERIAL PRIMARY KEY,
    equipo_id INTEGER NOT NULL REFERENCES equipos(id) ON DELETE CASCADE,
    nombre    VARCHAR(80) NOT NULL
);

CREATE TABLE asignaciones (
    id             SERIAL PRIMARY KEY,
    persona_id     INTEGER NOT NULL REFERENCES personas(id),
    equipo_id      INTEGER NOT NULL REFERENCES equipos(id),
    rol_equipo_id  INTEGER REFERENCES roles_equipo(id),
    servicio_id    INTEGER REFERENCES servicios(id),
    disponibilidad VARCHAR(255),
    activa         BOOLEAN   NOT NULL DEFAULT TRUE,
    creada_en      TIMESTAMP NOT NULL DEFAULT now()
);

-- ----------------------------- Formularios ----------------------------------
CREATE TABLE formularios (
    id          SERIAL PRIMARY KEY,
    nombre      VARCHAR(160) NOT NULL,
    descripcion VARCHAR(500),
    estado      VARCHAR(20)  NOT NULL DEFAULT 'borrador',
    slug        VARCHAR(20)  NOT NULL UNIQUE,
    creado_en   TIMESTAMP    NOT NULL DEFAULT now()
);
CREATE INDEX ix_formularios_slug ON formularios(slug);

CREATE TABLE campos_formulario (
    id            SERIAL PRIMARY KEY,
    formulario_id INTEGER NOT NULL REFERENCES formularios(id) ON DELETE CASCADE,
    etiqueta      VARCHAR(160) NOT NULL,
    tipo          VARCHAR(30)  NOT NULL DEFAULT 'texto',
    requerido     BOOLEAN      NOT NULL DEFAULT FALSE,
    opciones      JSON         NOT NULL DEFAULT '[]',
    orden         INTEGER      NOT NULL DEFAULT 0,
    mapea_a       VARCHAR(30)
);

CREATE TABLE respuestas_formulario (
    id            SERIAL PRIMARY KEY,
    formulario_id INTEGER NOT NULL REFERENCES formularios(id) ON DELETE CASCADE,
    persona_id    INTEGER REFERENCES personas(id),
    datos         JSON      NOT NULL DEFAULT '{}',
    fecha         TIMESTAMP NOT NULL DEFAULT now()
);

-- ------------------------------ Auditoría -----------------------------------
CREATE TABLE auditoria (
    id         SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id),
    accion     VARCHAR(80)  NOT NULL,
    entidad    VARCHAR(60),
    entidad_id VARCHAR(40),
    detalle    VARCHAR(600) NOT NULL DEFAULT '',
    ip         VARCHAR(60),
    fecha      TIMESTAMP    NOT NULL DEFAULT now()
);
CREATE INDEX ix_auditoria_fecha ON auditoria(fecha);
