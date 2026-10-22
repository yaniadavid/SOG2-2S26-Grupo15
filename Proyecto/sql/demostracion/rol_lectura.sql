-- Crea (o reconcilia) el rol de solo lectura sog2_lectura para la demostracion.
-- Ejecutar con un usuario que pueda crear roles y otorgar privilegios (por ejemplo odoo, miembro de cloudsqlsuperuser):
--   psql -X -q -v ON_ERROR_STOP=1 -v clave_lectura="$CLAVE_LECTURA" -f rol_lectura.sql
-- La contrasena llega solo como variable de psql; este archivo no la contiene.
-- Es idempotente: puede ejecutarse varias veces y deja los privilegios exactamente como la lista blanca de abajo.
\set ON_ERROR_STOP on

-- 1. Crear el rol solo si no existe (sin SUPERUSER, CREATEDB, CREATEROLE ni REPLICATION).
SELECT format('CREATE ROLE sog2_lectura LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION PASSWORD %L', :'clave_lectura')
WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'sog2_lectura')
\gexec

-- 2. Reconciliar el rol existente: login y contrasena vigentes, y sesiones de solo lectura por defecto.
SELECT format('ALTER ROLE sog2_lectura LOGIN PASSWORD %L', :'clave_lectura')
\gexec
ALTER ROLE sog2_lectura SET default_transaction_read_only = on;

-- 3. Partir de cero: retirar cualquier privilegio previo sobre tablas y esquema para que la lista blanca sea la unica fuente.
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM sog2_lectura;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM sog2_lectura;
REVOKE CREATE ON SCHEMA public FROM sog2_lectura;

-- 4. Conexion a la base actual y uso del esquema public (sin CREATE).
SELECT format('GRANT CONNECT ON DATABASE %I TO sog2_lectura', current_database())
\gexec
GRANT USAGE ON SCHEMA public TO sog2_lectura;

-- 5. LISTA BLANCA (solo SELECT). Sin ALTER DEFAULT PRIVILEGES: una tabla nueva no queda visible.
-- Tablas completas (datos de negocio sin informacion sensible de acceso):
GRANT SELECT ON sale_order TO sog2_lectura;
GRANT SELECT ON sale_order_line TO sog2_lectura;
GRANT SELECT ON purchase_order TO sog2_lectura;
GRANT SELECT ON purchase_order_line TO sog2_lectura;
GRANT SELECT ON account_move TO sog2_lectura;
GRANT SELECT ON account_move_line TO sog2_lectura;
GRANT SELECT ON product_template TO sog2_lectura;
GRANT SELECT ON product_product TO sog2_lectura;
GRANT SELECT ON hr_job TO sog2_lectura;
GRANT SELECT ON hr_department TO sog2_lectura;
GRANT SELECT ON res_currency TO sog2_lectura;
-- Por columnas (se evitan datos personales, contenido binario y datos bancarios):
GRANT SELECT (id, name, active, create_date) ON res_partner TO sog2_lectura;
GRANT SELECT (id, name, active, job_id, department_id, company_id, barcode, identification_id, create_date) ON hr_employee TO sog2_lectura;
GRANT SELECT (id, name, res_model, res_id, type, mimetype, file_size, company_id, create_date) ON ir_attachment TO sog2_lectura;
-- NO se otorga: res_users, res_users_apikeys, ir_config_parameter ni ninguna otra tabla fuera de esta lista.
