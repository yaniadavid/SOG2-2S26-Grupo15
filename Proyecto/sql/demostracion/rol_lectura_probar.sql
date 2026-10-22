-- Prueba del rol sog2_lectura. Ejecutar CONECTADO COMO sog2_lectura (no como odoo):
--   PGUSER=sog2_lectura PGPASSWORD="$CLAVE_LECTURA" psql -X -v ON_ERROR_STOP=0 -f rol_lectura_probar.sql
-- Cada bloque marcado "DEBE FALLAR" tiene que terminar con un ERROR de psql; si alguno devuelve exito, el rol esta mal configurado.
-- Se usa ON_ERROR_STOP=0 para ver todos los errores seguidos; las escrituras van en transacciones que se revierten por seguridad.
\pset null '-'
\pset pager off

\echo
\echo ===== PRUEBA DEL ROL sog2_lectura =====

\echo
\echo --- P0 Identidad y modo de sesion
-- QUE DEMUESTRA: que la sesion corre como sog2_lectura y que arranca en solo lectura.
SELECT current_user AS usuario, current_database() AS base, current_setting('default_transaction_read_only') AS solo_lectura;

\echo
\echo --- P1 SELECT permitido sobre una tabla de la lista blanca
-- QUE DEMUESTRA: que el rol puede leer los datos de la demostracion (debe devolver 50).
SELECT count(*) AS ventas_confirmadas_i1
FROM sale_order so
WHERE so.state = 'sale' AND so.client_order_ref LIKE 'I1-V-%';

\echo
\echo --- P2 INSERT (DEBE FALLAR: transaccion de solo lectura)
-- QUE DEMUESTRA: que la sesion no admite escrituras por defecto.
BEGIN;
INSERT INTO sale_order (name) VALUES ('PRUEBA-NO-DEBE-EXISTIR');
ROLLBACK;

\echo
\echo --- P3 UPDATE (DEBE FALLAR: permiso denegado aun forzando lectura/escritura)
-- QUE DEMUESTRA: que sin el privilegio UPDATE la escritura se rechaza aunque la sesion se ponga en lectura/escritura.
BEGIN;
SET LOCAL transaction_read_only = off;
UPDATE sale_order SET client_order_ref = 'PRUEBA-NO-DEBE-EXISTIR' WHERE id = -1;
ROLLBACK;

\echo
\echo --- P4 INSERT con lectura/escritura forzada (DEBE FALLAR: permiso denegado)
-- QUE DEMUESTRA: que el bloqueo de escritura depende de los privilegios y no solo del parametro de sesion.
BEGIN;
SET LOCAL transaction_read_only = off;
INSERT INTO sale_order (name) VALUES ('PRUEBA-NO-DEBE-EXISTIR');
ROLLBACK;

\echo
\echo --- P5 SELECT sobre res_users (DEBE FALLAR: permiso denegado)
-- QUE DEMUESTRA: que las credenciales y usuarios de Odoo no son legibles con este rol.
SELECT count(*) FROM res_users;

\echo
\echo --- P6 SELECT sobre ir_config_parameter (DEBE FALLAR: permiso denegado)
-- QUE DEMUESTRA: que los parametros de configuracion del sistema no son legibles con este rol.
SELECT count(*) FROM ir_config_parameter;

\echo
\echo --- P7 Columna sensible de res_partner (DEBE FALLAR: permiso denegado)
-- QUE DEMUESTRA: que el acceso por columnas oculta datos de contacto de terceros.
SELECT email FROM res_partner LIMIT 1;
