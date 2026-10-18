\set ON_ERROR_STOP on

BEGIN;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'sog2_owner') THEN
        CREATE ROLE sog2_owner NOLOGIN;
    END IF;
END
$$;

GRANT sog2_owner TO CURRENT_USER;
GRANT CONNECT, CREATE ON DATABASE :"DBNAME" TO sog2_owner;

CREATE SCHEMA IF NOT EXISTS staging AUTHORIZATION sog2_owner;
CREATE SCHEMA IF NOT EXISTS core AUTHORIZATION sog2_owner;
CREATE SCHEMA IF NOT EXISTS analytics AUTHORIZATION sog2_owner;
CREATE SCHEMA IF NOT EXISTS audit AUTHORIZATION sog2_owner;

ALTER SCHEMA staging OWNER TO sog2_owner;
ALTER SCHEMA core OWNER TO sog2_owner;
ALTER SCHEMA analytics OWNER TO sog2_owner;
ALTER SCHEMA audit OWNER TO sog2_owner;

ALTER TABLE IF EXISTS staging.ventas_online_limpio OWNER TO sog2_owner;

DO $$
DECLARE
    objeto RECORD;
BEGIN
    FOR objeto IN
        SELECT schemaname, tablename
        FROM pg_tables
        WHERE schemaname IN ('staging', 'core', 'analytics', 'audit')
    LOOP
        EXECUTE format('ALTER TABLE %I.%I OWNER TO sog2_owner', objeto.schemaname, objeto.tablename);
    END LOOP;

    FOR objeto IN
        SELECT schemaname, viewname
        FROM pg_views
        WHERE schemaname IN ('analytics')
    LOOP
        EXECUTE format('ALTER VIEW %I.%I OWNER TO sog2_owner', objeto.schemaname, objeto.viewname);
    END LOOP;

    FOR objeto IN
        SELECT sequence_schema, sequence_name
        FROM information_schema.sequences
        WHERE sequence_schema IN ('core', 'audit')
    LOOP
        EXECUTE format('ALTER SEQUENCE %I.%I OWNER TO sog2_owner', objeto.sequence_schema, objeto.sequence_name);
    END LOOP;
END
$$;

SET ROLE sog2_owner;

CREATE TABLE IF NOT EXISTS audit.cargas (
    carga_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    archivo_origen TEXT NOT NULL,
    sha256_origen CHAR(64) NOT NULL,
    version_reglas TEXT NOT NULL,
    filas_leidas INTEGER NOT NULL CHECK (filas_leidas >= 0),
    filas_cargadas INTEGER NOT NULL CHECK (filas_cargadas >= 0),
    filas_descartadas INTEGER NOT NULL CHECK (filas_descartadas >= 0),
    estado TEXT NOT NULL CHECK (estado IN ('en_proceso', 'completada', 'fallida')),
    cargado_por TEXT NOT NULL DEFAULT SESSION_USER,
    cargado_en TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_cargas_archivo_reglas UNIQUE (sha256_origen, version_reglas),
    CONSTRAINT ck_cargas_sha256 CHECK (sha256_origen ~ '^[0-9a-f]{64}$')
);

CREATE TABLE IF NOT EXISTS core.generos (
    codigo SMALLINT PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE,
    CONSTRAINT ck_generos_codigo CHECK (codigo IN (0, 1))
);

CREATE TABLE IF NOT EXISTS core.metodos_pago (
    codigo SMALLINT PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE,
    CONSTRAINT ck_metodos_pago_codigo CHECK (codigo IN (0, 1, 2))
);

CREATE TABLE IF NOT EXISTS core.navegadores (
    codigo SMALLINT PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE,
    CONSTRAINT ck_navegadores_codigo CHECK (codigo BETWEEN 0 AND 4)
);

INSERT INTO core.generos (codigo, nombre)
VALUES (0, 'Masculino'), (1, 'Femenino')
ON CONFLICT (codigo) DO UPDATE SET nombre = EXCLUDED.nombre;

INSERT INTO core.metodos_pago (codigo, nombre)
VALUES
    (0, 'Efectivo'),
    (1, 'Tarjeta de crédito'),
    (2, 'Tarjeta de débito')
ON CONFLICT (codigo) DO UPDATE SET nombre = EXCLUDED.nombre;

INSERT INTO core.navegadores (codigo, nombre)
VALUES
    (0, 'Tienda física'),
    (1, 'Navegador 1'),
    (2, 'Navegador 2'),
    (3, 'Navegador 3'),
    (4, 'Navegador 4')
ON CONFLICT (codigo) DO UPDATE SET nombre = EXCLUDED.nombre;

CREATE TABLE IF NOT EXISTS core.ventas_online (
    registro_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    carga_id BIGINT NOT NULL REFERENCES audit.cargas(carga_id),
    fila_origen INTEGER NOT NULL UNIQUE CHECK (fila_origen >= 2),
    id_cliente INTEGER NOT NULL CHECK (id_cliente > 0),
    edad SMALLINT CHECK (edad BETWEEN 1 AND 100),
    genero SMALLINT REFERENCES core.generos(codigo),
    venta_total NUMERIC(12, 2) NOT NULL,
    numero_compras SMALLINT NOT NULL CHECK (numero_compras >= 0),
    fecha_compra DATE NOT NULL,
    monto_compra NUMERIC(12, 2) NOT NULL,
    metodo_pago SMALLINT REFERENCES core.metodos_pago(codigo),
    tiempo NUMERIC(8, 2) NOT NULL CHECK (tiempo >= 0),
    navegador SMALLINT REFERENCES core.navegadores(codigo),
    boletin BOOLEAN,
    vale BOOLEAN,
    hash_fila CHAR(64) NOT NULL UNIQUE,
    cargado_en TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_ventas_hash CHECK (hash_fila ~ '^[0-9a-f]{64}$')
);

CREATE TABLE IF NOT EXISTS audit.problemas_calidad (
    registro_id BIGINT NOT NULL REFERENCES core.ventas_online(registro_id) ON DELETE CASCADE,
    problema TEXT NOT NULL,
    PRIMARY KEY (registro_id, problema)
);

CREATE TABLE IF NOT EXISTS staging.ventas_online_limpio (
    fila_origen TEXT,
    id_cliente TEXT,
    edad TEXT,
    genero TEXT,
    venta_total TEXT,
    numero_compras TEXT,
    fecha_compra TEXT,
    monto_compra TEXT,
    metodo_pago TEXT,
    tiempo TEXT,
    navegador TEXT,
    boletin TEXT,
    vale TEXT,
    problemas_calidad TEXT,
    hash_fila TEXT
);

CREATE INDEX IF NOT EXISTS idx_ventas_fecha ON core.ventas_online(fecha_compra);
CREATE INDEX IF NOT EXISTS idx_ventas_cliente ON core.ventas_online(id_cliente);
CREATE INDEX IF NOT EXISTS idx_ventas_metodo_pago ON core.ventas_online(metodo_pago);
CREATE INDEX IF NOT EXISTS idx_ventas_navegador ON core.ventas_online(navegador);
CREATE INDEX IF NOT EXISTS idx_ventas_edad ON core.ventas_online(edad);

CREATE OR REPLACE VIEW analytics.ventas_detalle AS
SELECT
    v.registro_id,
    v.id_cliente,
    v.edad,
    v.genero AS genero_codigo,
    g.nombre AS genero,
    v.venta_total,
    v.numero_compras,
    v.fecha_compra,
    EXTRACT(YEAR FROM v.fecha_compra)::INTEGER AS anio,
    EXTRACT(MONTH FROM v.fecha_compra)::INTEGER AS mes,
    v.monto_compra,
    v.metodo_pago AS metodo_pago_codigo,
    mp.nombre AS metodo_pago,
    v.tiempo,
    v.navegador AS navegador_codigo,
    n.nombre AS navegador,
    v.boletin,
    v.vale
FROM core.ventas_online AS v
LEFT JOIN core.generos AS g ON g.codigo = v.genero
LEFT JOIN core.metodos_pago AS mp ON mp.codigo = v.metodo_pago
LEFT JOIN core.navegadores AS n ON n.codigo = v.navegador;

RESET ROLE;
REVOKE sog2_owner FROM CURRENT_USER;

COMMIT;
