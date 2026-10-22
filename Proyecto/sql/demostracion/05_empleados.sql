\echo
\echo ===== 05. EMPLEADOS =====

\echo
\echo --- 05.1 Empleados activos por cargo
-- QUE DEMUESTRA: la plantilla distribuida por puesto (incluye cargos sin empleados con 0).
SELECT coalesce(to_jsonb(j.name)->>'en_US', to_jsonb(j.name)#>>'{}') AS cargo,
       count(e.id) AS empleados
FROM hr_job j
LEFT JOIN hr_employee e ON e.job_id = j.id AND e.active
WHERE j.active
GROUP BY j.id, 1
ORDER BY empleados DESC, cargo;

\echo
\echo --- 05.2 Empleados activos por departamento
-- QUE DEMUESTRA: la plantilla distribuida por departamento (incluye departamentos vacios con 0).
SELECT coalesce(to_jsonb(d.name)->>'en_US', to_jsonb(d.name)#>>'{}') AS departamento,
       count(e.id) AS empleados
FROM hr_department d
LEFT JOIN hr_employee e ON e.department_id = d.id AND e.active
WHERE d.active
GROUP BY d.id, 1
ORDER BY empleados DESC, departamento;

\echo
\echo --- 05.3 Empleados por departamento y cargo
-- QUE DEMUESTRA: la estructura organizacional cruzada (departamento x cargo).
SELECT coalesce(to_jsonb(d.name)->>'en_US', to_jsonb(d.name)#>>'{}', '(sin departamento)') AS departamento,
       coalesce(to_jsonb(j.name)->>'en_US', to_jsonb(j.name)#>>'{}', '(sin cargo)')         AS cargo,
       count(*) AS empleados
FROM hr_employee e
LEFT JOIN hr_department d ON d.id = e.department_id
LEFT JOIN hr_job j        ON j.id = e.job_id
WHERE e.active
GROUP BY d.id, j.id, 1, 2
ORDER BY 1, 2;
