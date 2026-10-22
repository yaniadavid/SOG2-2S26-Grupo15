\echo
\echo ===== 01. CONTEOS POR REQUISITO DEL ENUNCIADO =====
-- QUE DEMUESTRA: una fila por requisito con el conteo actual de TODA la base,
-- la porcion del Integrante 1 (prefijo I1-) y el minimo exigido; "cumple" compara base vs minimo.
-- Definiciones: ventas = sale.order confirmadas (state 'sale'); cotizaciones = state draft/sent;
-- compras con factura = ordenes de compra confirmadas (purchase/done) con factura de proveedor
-- publicada vinculada por purchase_line_id; facturas = facturas de cliente publicadas;
-- materiales = plantillas de producto activas que se compran y no se venden (insumos de sucursal).
WITH compras_con_factura AS (
    SELECT DISTINCT po.id, po.partner_ref, po.origin
    FROM purchase_order po
    JOIN purchase_order_line pol ON pol.order_id = po.id
    JOIN account_move_line aml   ON aml.purchase_line_id = pol.id
    JOIN account_move am         ON am.id = aml.move_id
    WHERE po.state IN ('purchase', 'done')
      AND am.move_type = 'in_invoice'
      AND am.state = 'posted'
)
SELECT 1 AS n, 'Ventas (ordenes confirmadas)' AS requisito,
       count(*) AS total_base,
       count(*) FILTER (WHERE so.client_order_ref LIKE 'I1-%') AS porcion_i1,
       150 AS minimo, count(*) >= 150 AS cumple
FROM sale_order so WHERE so.state = 'sale'
UNION ALL
SELECT 2, 'Cotizaciones (borrador o enviada)',
       count(*), count(*) FILTER (WHERE so.client_order_ref LIKE 'I1-%'),
       20, count(*) >= 20
FROM sale_order so WHERE so.state IN ('draft', 'sent')
UNION ALL
SELECT 3, 'Empleados activos',
       count(*),
       count(*) FILTER (WHERE e.name LIKE 'I1-%' OR e.barcode LIKE 'I1-%' OR e.identification_id LIKE 'I1-%'),
       35, count(*) >= 35
FROM hr_employee e WHERE e.active
UNION ALL
SELECT 4, 'Cargos (puestos) activos',
       count(*),
       count(*) FILTER (WHERE coalesce(to_jsonb(j.name)->>'en_US', to_jsonb(j.name)#>>'{}') IN ('Cajero de Sucursal', 'Analista de Compras')),
       6, count(*) >= 6
FROM hr_job j WHERE j.active
UNION ALL
SELECT 5, 'Departamentos activos',
       count(*),
       count(*) FILTER (WHERE coalesce(to_jsonb(d.name)->>'en_US', to_jsonb(d.name)#>>'{}') IN ('Operaciones de Tienda', 'Administracion y Compras')),
       5, count(*) >= 5
FROM hr_department d WHERE d.active
UNION ALL
SELECT 6, 'Compras con factura de proveedor',
       count(*),
       count(*) FILTER (WHERE c.partner_ref LIKE 'I1-%' OR c.origin LIKE 'I1-%'),
       100, count(*) >= 100
FROM compras_con_factura c
UNION ALL
SELECT 7, 'Materiales (productos comprables)',
       count(*) FILTER (WHERE NOT pt.sale_ok),
       count(*) FILTER (WHERE NOT pt.sale_ok AND pt.default_code LIKE 'I1-MAT-%'),
       60, count(*) FILTER (WHERE NOT pt.sale_ok) >= 60
FROM product_template pt WHERE pt.active AND pt.purchase_ok
UNION ALL
SELECT 8, 'Facturas de cliente publicadas',
       count(*),
       count(*) FILTER (WHERE am.ref LIKE 'I1-%' OR am.invoice_origin LIKE 'I1-%' OR am.payment_reference LIKE 'I1-%'),
       50, count(*) >= 50
FROM account_move am WHERE am.move_type = 'out_invoice' AND am.state = 'posted'
ORDER BY n;
