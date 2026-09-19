\set ON_ERROR_STOP on

GRANT sog2_loader TO CURRENT_USER;
SET ROLE sog2_loader;

TRUNCATE staging.ventas_online_limpio;

\copy staging.ventas_online_limpio (fila_origen, id_cliente, edad, genero, venta_total, numero_compras, fecha_compra, monto_compra, metodo_pago, tiempo, navegador, boletin, vale, problemas_calidad, hash_fila) FROM 'data/processed/ventas_online_2025_limpio.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')

DO $$
DECLARE
    total INTEGER;
BEGIN
    SELECT COUNT(*) INTO total FROM staging.ventas_online_limpio;
    IF total <> 1003 THEN
        RAISE EXCEPTION 'Se esperaban 1003 filas limpias y se recibieron %.', total;
    END IF;
END
$$;

BEGIN;

INSERT INTO audit.cargas (
    archivo_origen,
    sha256_origen,
    version_reglas,
    filas_leidas,
    filas_cargadas,
    filas_descartadas,
    estado
)
VALUES (
    'ventas_online_2025.csv',
    'a83e8c253c018d27f68d972436687c86fd64e04dd8d61db2dd409e0ff765a703',
    '1.0',
    1008,
    0,
    5,
    'en_proceso'
)
ON CONFLICT (sha256_origen, version_reglas) DO UPDATE
SET
    filas_leidas = EXCLUDED.filas_leidas,
    filas_cargadas = 0,
    filas_descartadas = EXCLUDED.filas_descartadas,
    estado = 'en_proceso',
    cargado_por = SESSION_USER,
    cargado_en = CURRENT_TIMESTAMP;

DELETE FROM core.ventas_online
WHERE carga_id = (
    SELECT carga_id
    FROM audit.cargas
    WHERE sha256_origen = 'a83e8c253c018d27f68d972436687c86fd64e04dd8d61db2dd409e0ff765a703'
      AND version_reglas = '1.0'
)
AND fila_origen NOT IN (
    SELECT fila_origen::INTEGER FROM staging.ventas_online_limpio
);

INSERT INTO core.ventas_online (
    carga_id,
    fila_origen,
    id_cliente,
    edad,
    genero,
    venta_total,
    numero_compras,
    fecha_compra,
    monto_compra,
    metodo_pago,
    tiempo,
    navegador,
    boletin,
    vale,
    hash_fila
)
SELECT
    c.carga_id,
    s.fila_origen::INTEGER,
    s.id_cliente::INTEGER,
    NULLIF(s.edad, '')::SMALLINT,
    NULLIF(s.genero, '')::SMALLINT,
    s.venta_total::NUMERIC(12, 2),
    s.numero_compras::SMALLINT,
    s.fecha_compra::DATE,
    s.monto_compra::NUMERIC(12, 2),
    NULLIF(s.metodo_pago, '')::SMALLINT,
    s.tiempo::NUMERIC(8, 2),
    NULLIF(s.navegador, '')::SMALLINT,
    CASE s.boletin WHEN '1' THEN TRUE WHEN '0' THEN FALSE ELSE NULL END,
    CASE s.vale WHEN '1' THEN TRUE WHEN '0' THEN FALSE ELSE NULL END,
    s.hash_fila
FROM staging.ventas_online_limpio AS s
CROSS JOIN audit.cargas AS c
WHERE c.sha256_origen = 'a83e8c253c018d27f68d972436687c86fd64e04dd8d61db2dd409e0ff765a703'
  AND c.version_reglas = '1.0'
ON CONFLICT (fila_origen) DO UPDATE
SET
    carga_id = EXCLUDED.carga_id,
    id_cliente = EXCLUDED.id_cliente,
    edad = EXCLUDED.edad,
    genero = EXCLUDED.genero,
    venta_total = EXCLUDED.venta_total,
    numero_compras = EXCLUDED.numero_compras,
    fecha_compra = EXCLUDED.fecha_compra,
    monto_compra = EXCLUDED.monto_compra,
    metodo_pago = EXCLUDED.metodo_pago,
    tiempo = EXCLUDED.tiempo,
    navegador = EXCLUDED.navegador,
    boletin = EXCLUDED.boletin,
    vale = EXCLUDED.vale,
    hash_fila = EXCLUDED.hash_fila,
    cargado_en = CURRENT_TIMESTAMP;

DELETE FROM audit.problemas_calidad AS p
USING core.ventas_online AS v
WHERE p.registro_id = v.registro_id
  AND v.carga_id = (
      SELECT carga_id
      FROM audit.cargas
      WHERE sha256_origen = 'a83e8c253c018d27f68d972436687c86fd64e04dd8d61db2dd409e0ff765a703'
        AND version_reglas = '1.0'
  );

INSERT INTO audit.problemas_calidad (registro_id, problema)
SELECT v.registro_id, problema
FROM staging.ventas_online_limpio AS s
JOIN core.ventas_online AS v ON v.fila_origen = s.fila_origen::INTEGER
CROSS JOIN LATERAL string_to_table(s.problemas_calidad, '|') AS problema
WHERE NULLIF(s.problemas_calidad, '') IS NOT NULL
ON CONFLICT DO NOTHING;

UPDATE audit.cargas
SET
    filas_cargadas = (
        SELECT COUNT(*)
        FROM core.ventas_online AS v
        WHERE v.carga_id = audit.cargas.carga_id
    ),
    estado = 'completada'
WHERE sha256_origen = 'a83e8c253c018d27f68d972436687c86fd64e04dd8d61db2dd409e0ff765a703'
  AND version_reglas = '1.0';

COMMIT;

SELECT
    c.filas_leidas,
    c.filas_cargadas,
    c.filas_descartadas,
    c.estado
FROM audit.cargas AS c
WHERE c.sha256_origen = 'a83e8c253c018d27f68d972436687c86fd64e04dd8d61db2dd409e0ff765a703'
  AND c.version_reglas = '1.0';

RESET ROLE;
REVOKE sog2_loader FROM CURRENT_USER;
