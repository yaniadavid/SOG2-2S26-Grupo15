-- Comprobación de Empleados en la base PostgreSQL de Odoo.
-- Solo lectura. Ejemplo: psql ... -d quetzalmart_db -f Proyecto/sql/validar_empleados.sql

SELECT
    COUNT(*) FILTER (WHERE e.active) AS empleados_activos,
    COUNT(*) FILTER (WHERE e.active AND e.department_id IS NOT NULL AND e.job_id IS NOT NULL)
        AS activos_con_cargo_y_departamento,
    COUNT(*) FILTER (WHERE e.active AND j.department_id = e.department_id)
        AS activos_con_cargo_del_mismo_departamento,
    COUNT(*) FILTER (WHERE e.active AND e.job_id IS NULL) AS activos_sin_cargo,
    COUNT(*) FILTER (WHERE e.active AND e.department_id IS NULL) AS activos_sin_departamento
FROM hr_employee AS e
LEFT JOIN hr_job AS j ON j.id = e.job_id;

SELECT
    (SELECT COUNT(*) FROM hr_department WHERE active) AS departamentos_activos,
    (SELECT COUNT(*) FROM hr_department
     WHERE active AND name->>'en_US' IN (
         'Operaciones de Tienda', 'Administracion y Compras',
         'Logística e Inventario', 'Atención al Cliente',
         'Marketing y Comercio Digital')) AS departamentos_del_proyecto,
    (SELECT COUNT(*) FROM hr_job) AS cargos,
    (SELECT COUNT(*) FROM hr_job WHERE name->>'en_US' IN (
         'Cajero de Sucursal', 'Analista de Compras', 'Supervisor de Tienda',
         'Coordinador de Logística', 'Auxiliar de Almacén',
         'Agente de Atención al Cliente', 'Especialista de Marketing Digital'))
        AS cargos_del_proyecto,
    (SELECT COUNT(*) FROM ir_model_data
     WHERE module = 'quetzalmart_hr' AND model = 'hr.employee') AS empleados_cargados_por_este_lote;

SELECT
    COALESCE(d.name->>'es_GT', d.name->>'es_ES', d.name->>'en_US') AS departamento,
    COALESCE(j.name->>'es_GT', j.name->>'es_ES', j.name->>'en_US') AS cargo,
    COUNT(*) AS empleados_activos
FROM hr_employee AS e
JOIN hr_department AS d ON d.id = e.department_id
JOIN hr_job AS j ON j.id = e.job_id
WHERE e.active
GROUP BY d.id, d.name, j.id, j.name
ORDER BY departamento, cargo;
