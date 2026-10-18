\set ON_ERROR_STOP on

BEGIN;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'sog2_migrator') THEN
        CREATE ROLE sog2_migrator NOLOGIN;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'sog2_loader') THEN
        CREATE ROLE sog2_loader NOLOGIN;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'sog2_analyst_ro') THEN
        CREATE ROLE sog2_analyst_ro NOLOGIN;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'sog2_mcp_ro') THEN
        CREATE ROLE sog2_mcp_ro NOLOGIN;
    END IF;
END
$$;

GRANT sog2_owner TO sog2_migrator;
GRANT sog2_owner TO CURRENT_USER;

REVOKE CONNECT ON DATABASE :"DBNAME" FROM PUBLIC;
GRANT CONNECT ON DATABASE :"DBNAME"
TO sog2_owner, sog2_migrator, sog2_loader, sog2_analyst_ro, sog2_mcp_ro;

REVOKE ALL ON SCHEMA public FROM PUBLIC;

SET ROLE sog2_owner;

REVOKE ALL ON SCHEMA staging, core, analytics, audit FROM PUBLIC;
REVOKE ALL ON ALL TABLES IN SCHEMA staging, core, analytics, audit FROM PUBLIC;

GRANT USAGE ON SCHEMA staging, core, audit TO sog2_loader;
GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE
ON staging.ventas_online_limpio TO sog2_loader;
GRANT SELECT ON core.generos, core.metodos_pago, core.navegadores TO sog2_loader;
GRANT SELECT, INSERT, UPDATE, DELETE ON core.ventas_online TO sog2_loader;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA core TO sog2_loader;
GRANT SELECT, INSERT, UPDATE ON audit.cargas TO sog2_loader;
GRANT SELECT, INSERT, DELETE ON audit.problemas_calidad TO sog2_loader;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA audit TO sog2_loader;

GRANT USAGE ON SCHEMA core, analytics TO sog2_analyst_ro;
GRANT SELECT ON ALL TABLES IN SCHEMA core, analytics TO sog2_analyst_ro;

GRANT USAGE ON SCHEMA analytics TO sog2_mcp_ro;
GRANT SELECT ON ALL TABLES IN SCHEMA analytics TO sog2_mcp_ro;

ALTER DEFAULT PRIVILEGES FOR ROLE sog2_owner IN SCHEMA core
GRANT SELECT ON TABLES TO sog2_analyst_ro;
ALTER DEFAULT PRIVILEGES FOR ROLE sog2_owner IN SCHEMA analytics
GRANT SELECT ON TABLES TO sog2_analyst_ro, sog2_mcp_ro;

RESET ROLE;
REVOKE sog2_owner FROM CURRENT_USER;

COMMIT;
