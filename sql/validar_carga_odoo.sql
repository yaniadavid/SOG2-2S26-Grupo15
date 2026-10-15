-- Script de validación de datos cargados en Odoo
-- Ejecutar en PostgreSQL contra la base de datos quetzalmart_db

\echo '=========================================='
\echo 'VALIDACIÓN DE CARGA DE DATOS EN ODOO'
\echo '=========================================='

\echo ''
\echo '[1] Conteo de productos'
SELECT COUNT(*) as total_productos FROM product_product WHERE active = true;

\echo ''
\echo '[2] Conteo de clientes'
SELECT COUNT(*) as total_clientes FROM res_partner WHERE customer_rank > 0;

\echo ''
\echo '[3] Conteo de proveedores'
SELECT COUNT(*) as total_proveedores FROM res_partner WHERE supplier_rank > 0;

\echo ''
\echo '[4] Conteo de cargos'
SELECT COUNT(*) as total_cargos FROM hr_job;

\echo ''
\echo '[5] Conteo de departamentos'
SELECT COUNT(*) as total_departamentos FROM hr_department WHERE active = true;

\echo ''
\echo '[6] Conteo de empleados'
SELECT COUNT(*) as total_empleados FROM hr_employee WHERE active = true;

\echo ''
\echo '[7] Conteo de órdenes de venta'
SELECT COUNT(*) as total_ordenes_venta FROM sale_order WHERE state = 'sale';

\echo ''
\echo '[8] Conteo de presupuestos (órdenes en draft)'
SELECT COUNT(*) as total_presupuestos FROM sale_order WHERE state = 'draft';

\echo ''
\echo '[9] Conteo de órdenes de compra'
SELECT COUNT(*) as total_ordenes_compra FROM purchase_order;

\echo ''
\echo '[10] Conteo de facturas'
SELECT COUNT(*) as total_facturas FROM account_move WHERE move_type LIKE 'out_%';

\echo ''
\echo '=========================================='
\echo 'RESUMEN GENERAL'
\echo '=========================================='

SELECT
    (SELECT COUNT(*) FROM product_product WHERE active = true) as productos,
    (SELECT COUNT(*) FROM res_partner WHERE customer_rank > 0) as clientes,
    (SELECT COUNT(*) FROM res_partner WHERE supplier_rank > 0) as proveedores,
    (SELECT COUNT(*) FROM hr_job) as cargos,
    (SELECT COUNT(*) FROM hr_department WHERE active = true) as departamentos,
    (SELECT COUNT(*) FROM hr_employee WHERE active = true) as empleados,
    (SELECT COUNT(*) FROM sale_order WHERE state = 'sale') as ordenes_venta,
    (SELECT COUNT(*) FROM sale_order WHERE state = 'draft') as presupuestos,
    (SELECT COUNT(*) FROM purchase_order) as ordenes_compra,
    (SELECT COUNT(*) FROM account_move WHERE move_type LIKE 'out_%') as facturas;

\echo ''
\echo '=========================================='
\echo 'CONSULTAS ADICIONALES'
\echo '=========================================='

\echo ''
\echo 'Productos con mayor precio:'
SELECT name, list_price FROM product_product
WHERE active = true
ORDER BY list_price DESC LIMIT 5;

\echo ''
\echo 'Clientes registrados:'
SELECT name, email, phone FROM res_partner
WHERE customer_rank > 0 LIMIT 10;

\echo ''
\echo 'Proveedores registrados:'
SELECT name, email, phone FROM res_partner
WHERE supplier_rank > 0;

\echo ''
\echo 'Empleados con sus cargos y departamentos:'
SELECT
    e.name as empleado,
    j.name as cargo,
    d.name as departamento,
    e.email
FROM hr_employee e
LEFT JOIN hr_job j ON e.job_id = j.id
LEFT JOIN hr_department d ON e.department_id = d.id
WHERE e.active = true
ORDER BY e.name;

\echo ''
\echo 'Órdenes de venta confirmadas:'
SELECT
    so.id,
    so.name,
    rp.name as cliente,
    so.amount_total,
    so.state,
    so.create_date
FROM sale_order so
JOIN res_partner rp ON so.partner_id = rp.id
WHERE so.state = 'sale'
ORDER BY so.create_date DESC LIMIT 10;

\echo ''
\echo 'Órdenes de compra:'
SELECT
    po.id,
    po.name,
    rp.name as proveedor,
    po.amount_total,
    po.state,
    po.create_date
FROM purchase_order po
JOIN res_partner rp ON po.partner_id = rp.id
ORDER BY po.create_date DESC LIMIT 10;

\echo ''
\echo 'VALIDACIÓN COMPLETADA'
\echo '=========================================='
