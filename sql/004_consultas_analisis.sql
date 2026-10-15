-- ============================================================================
-- CONSULTAS SQL ANALÍTICAS - QUETZALMART_DB
-- Base de datos: quetzalmart_db (PostgreSQL en Cloud SQL)
-- Propósito: Análisis de ventas, compras y operaciones en Odoo 18
-- ============================================================================

-- CONSULTA 1: Total de Ventas por Mes (2024-2025)
-- Agrupa órdenes de venta finalizadas por mes calendario
-- Muestra cantidad de órdenes y valor total vendido
SELECT
    DATE_TRUNC('month', so.create_date)::date as mes,
    COUNT(*) as cantidad_ordenes,
    SUM(so.amount_total) as total_venta,
    ROUND(AVG(so.amount_total), 2) as promedio_orden,
    COUNT(DISTINCT so.partner_id) as clientes_unicos
FROM
    sale_order so
WHERE
    so.state IN ('sale', 'done')
    AND so.create_date >= '2024-01-01'
GROUP BY
    DATE_TRUNC('month', so.create_date)
ORDER BY
    mes DESC;

-- CONSULTA 2: Top 5 Productos Más Vendidos
-- Muestra los 5 productos con mayor cantidad vendida
-- Incluye valor total de ventas por producto
SELECT
    pt.name as producto,
    pt.id as producto_id,
    SUM(sol.product_uom_qty) as cantidad_vendida,
    COUNT(DISTINCT so.id) as numero_ordenes,
    SUM(sol.price_subtotal) as valor_total,
    ROUND(AVG(sol.price_unit), 2) as precio_promedio
FROM
    sale_order_line sol
    INNER JOIN sale_order so ON sol.order_id = so.id
    INNER JOIN product_product pp ON sol.product_id = pp.id
    INNER JOIN product_template pt ON pp.product_tmpl_id = pt.id
WHERE
    so.state IN ('sale', 'done')
GROUP BY
    pt.id, pt.name
ORDER BY
    cantidad_vendida DESC
LIMIT 5;

-- CONSULTA 3: Total de Ventas por Cliente
-- Resumen de actividad de compra por cliente
-- Incluye monto total, número de órdenes y fecha última compra
SELECT
    rc.name as cliente,
    rc.id as cliente_id,
    COUNT(so.id) as numero_ordenes,
    SUM(so.amount_total) as total_compras,
    ROUND(AVG(so.amount_total), 2) as promedio_compra,
    MAX(so.create_date)::date as ultima_compra,
    MIN(so.create_date)::date as primera_compra
FROM
    sale_order so
    INNER JOIN res_partner rc ON so.partner_id = rc.id
WHERE
    so.state IN ('sale', 'done')
GROUP BY
    rc.id, rc.name
ORDER BY
    total_compras DESC
LIMIT 20;

-- CONSULTA 4: Órdenes de Compra por Proveedor
-- Análisis de actividad de compra con cada proveedor
-- Muestra total comprado, cantidad de órdenes y estado actual
SELECT
    rp.name as proveedor,
    rp.id as proveedor_id,
    COUNT(po.id) as numero_ordenes,
    SUM(po.amount_total) as total_comprado,
    ROUND(AVG(po.amount_total), 2) as promedio_orden,
    po.state as estado_actual,
    COUNT(*) FILTER (WHERE po.state = 'purchase') as pendientes,
    COUNT(*) FILTER (WHERE po.state = 'done') as completadas
FROM
    purchase_order po
    INNER JOIN res_partner rp ON po.partner_id = rp.id
GROUP BY
    rp.id, rp.name, po.state
ORDER BY
    total_comprado DESC;

-- CONSULTA 5: Facturas Pendientes de Pago
-- Resumen de facturas no pagadas, por vencer o vencidas
-- Útil para gestión de cobranza
SELECT
    am.id as factura_id,
    am.name as numero_factura,
    rc.name as cliente,
    am.amount_total as monto_total,
    am.amount_residual as saldo_pendiente,
    am.invoice_date as fecha_factura,
    am.invoice_date_due::date as fecha_vencimiento,
    CASE
        WHEN am.invoice_date_due < CURRENT_DATE THEN 'VENCIDA'
        WHEN am.invoice_date_due <= CURRENT_DATE + INTERVAL '7 days' THEN 'POR VENCER'
        ELSE 'EN PLAZO'
    END as estado_pago,
    (CURRENT_DATE - am.invoice_date_due::date) as dias_atraso
FROM
    account_move am
    INNER JOIN res_partner rc ON am.partner_id = rc.id
WHERE
    am.move_type = 'out_invoice'
    AND am.state = 'posted'
    AND am.amount_residual > 0
ORDER BY
    am.invoice_date_due ASC;

-- CONSULTA 6: Empleados por Departamento
-- Distribución de recursos humanos
-- Muestra activos, inactivos y costo total
SELECT
    hd.name as departamento,
    hd.id as departamento_id,
    COUNT(he.id) as total_empleados,
    COUNT(CASE WHEN he.active = true THEN 1 END) as empleados_activos,
    COUNT(CASE WHEN he.active = false THEN 1 END) as empleados_inactivos,
    ROUND(SUM(COALESCE(hc.wage, 0))::numeric, 2) as costo_mensual_total,
    ROUND(AVG(COALESCE(hc.wage, 0))::numeric, 2) as salario_promedio
FROM
    hr_department hd
    LEFT JOIN hr_employee he ON hd.id = he.department_id
    LEFT JOIN hr_contract hc ON he.id = hc.employee_id
        AND hc.state = 'open'
        AND hc.date_end IS NULL
GROUP BY
    hd.id, hd.name
ORDER BY
    total_empleados DESC;

-- ============================================================================
-- CONSULTAS ADICIONALES PARA VALIDACIÓN DE DATOS
-- ============================================================================

-- CONSULTA VALIDACIÓN 1: Conteo de Registros Principales
SELECT
    'Órdenes de Venta' as tipo_registro,
    COUNT(*) as total
FROM sale_order
UNION ALL
SELECT
    'Líneas de Venta',
    COUNT(*)
FROM sale_order_line
UNION ALL
SELECT
    'Órdenes de Compra',
    COUNT(*)
FROM purchase_order
UNION ALL
SELECT
    'Facturas',
    COUNT(*)
FROM account_move
WHERE move_type IN ('out_invoice', 'in_invoice')
UNION ALL
SELECT
    'Clientes',
    COUNT(*)
FROM res_partner
WHERE customer_rank > 0
UNION ALL
SELECT
    'Proveedores',
    COUNT(*)
FROM res_partner
WHERE supplier_rank > 0
UNION ALL
SELECT
    'Empleados',
    COUNT(*)
FROM hr_employee
WHERE active = true
UNION ALL
SELECT
    'Productos',
    COUNT(*)
FROM product_template
WHERE active = true;

-- CONSULTA VALIDACIÓN 2: Período de Datos
SELECT
    'Órdenes de Venta' as fuente,
    MIN(create_date)::date as fecha_minima,
    MAX(create_date)::date as fecha_maxima,
    COUNT(*) as cantidad
FROM sale_order
WHERE state IN ('sale', 'done')
UNION ALL
SELECT
    'Órdenes de Compra',
    MIN(create_date)::date,
    MAX(create_date)::date,
    COUNT(*)
FROM purchase_order
UNION ALL
SELECT
    'Facturas',
    MIN(invoice_date),
    MAX(invoice_date),
    COUNT(*)
FROM account_move
WHERE move_type IN ('out_invoice', 'in_invoice');

-- ============================================================================
-- CONSULTA BONIFICACIÓN: Dashboard Resumen Ejecutivo
-- ============================================================================

SELECT
    'PERÍODO ANALIZADO' as seccion,
    TO_CHAR(MIN(create_date), 'YYYY-MM-DD') || ' a ' ||
    TO_CHAR(MAX(create_date), 'YYYY-MM-DD') as descripcion,
    COUNT(DISTINCT DATE_TRUNC('month', create_date)) as meses
FROM sale_order
WHERE state IN ('sale', 'done')
UNION ALL
SELECT
    'INGRESOS TOTALES',
    'Q' || ROUND(SUM(amount_total)::numeric, 2)::text,
    COUNT(*)
FROM sale_order
WHERE state IN ('sale', 'done')
UNION ALL
SELECT
    'TRANSACCIONES PROMEDIO',
    'Q' || ROUND(AVG(amount_total)::numeric, 2)::text,
    0
FROM sale_order
WHERE state IN ('sale', 'done')
UNION ALL
SELECT
    'CLIENTES ACTIVOS',
    COUNT(DISTINCT partner_id)::text,
    0
FROM sale_order
WHERE state IN ('sale', 'done')
    AND create_date >= CURRENT_DATE - INTERVAL '90 days';
