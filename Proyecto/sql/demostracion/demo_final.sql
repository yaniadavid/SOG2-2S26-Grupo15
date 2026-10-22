-- Demostracion en vivo: los 6 grupos de verificacion en version compacta y un bloque final de TOTALES.
-- Solo lectura. Pensado para una pantalla: cada consulta limita sus filas.
-- Uso: psql -X -q -v ON_ERROR_STOP=1 -f demo_final.sql (puede usarse con el rol sog2_lectura).
-- El propio archivo abre BEGIN READ ONLY y termina con ROLLBACK.
\pset null '-'
\pset pager off
BEGIN READ ONLY;

\echo
\echo ===== 1. CONTEOS POR REQUISITO (toda la base vs minimo del enunciado) =====
-- QUE DEMUESTRA: el avance de cada requisito del enunciado; "cumple" compara el total de la base con el minimo.
SELECT 'Ventas confirmadas' AS requisito, count(*) AS total_base, 150 AS minimo, count(*) >= 150 AS cumple
FROM sale_order so WHERE so.state = 'sale'
UNION ALL
SELECT 'Cotizaciones', count(*), 20, count(*) >= 20
FROM sale_order so WHERE so.state IN ('draft', 'sent')
UNION ALL
SELECT 'Empleados activos', count(*), 35, count(*) >= 35
FROM hr_employee e WHERE e.active
UNION ALL
SELECT 'Cargos activos', count(*), 6, count(*) >= 6
FROM hr_job j WHERE j.active
UNION ALL
SELECT 'Departamentos activos', count(*), 5, count(*) >= 5
FROM hr_department d WHERE d.active
UNION ALL
SELECT 'Materiales (comprables, no vendibles)', count(*), 60, count(*) >= 60
FROM product_template pt WHERE pt.active AND pt.purchase_ok AND NOT pt.sale_ok
UNION ALL
SELECT 'Facturas de cliente publicadas', count(*), 50, count(*) >= 50
FROM account_move am WHERE am.move_type = 'out_invoice' AND am.state = 'posted';

\echo
\echo ===== 2. VENTAS =====
-- QUE DEMUESTRA: el embudo comercial; cada estado de sale.order con su cantidad y monto.
SELECT so.state AS estado, count(*) AS ordenes, round(sum(so.amount_total), 2) AS total
FROM sale_order so
GROUP BY so.state
ORDER BY so.state;

-- QUE DEMUESTRA: la distribucion temporal de las ventas confirmadas (maximo 12 meses).
SELECT to_char(date_trunc('month', so.date_order), 'YYYY-MM') AS mes,
       count(*) AS ordenes, round(sum(so.amount_total), 2) AS total
FROM sale_order so
WHERE so.state = 'sale'
GROUP BY 1
ORDER BY 1
LIMIT 12;

\echo
\echo ===== 3. COMPRAS =====
-- QUE DEMUESTRA: compras confirmadas y cuantas ya tienen factura de proveedor vinculada.
SELECT count(*) AS compras_confirmadas,
       count(*) FILTER (WHERE EXISTS (
           SELECT 1
           FROM purchase_order_line pol
           JOIN account_move_line aml ON aml.purchase_line_id = pol.id
           JOIN account_move am       ON am.id = aml.move_id
           WHERE pol.order_id = po.id AND am.move_type = 'in_invoice' AND am.state <> 'cancel'
       )) AS con_factura
FROM purchase_order po
WHERE po.state IN ('purchase', 'done');

-- QUE DEMUESTRA: los 5 proveedores con mayor monto comprado.
SELECT coalesce(to_jsonb(rp.name)->>'en_US', to_jsonb(rp.name)#>>'{}') AS proveedor,
       count(*) AS ordenes, round(sum(po.amount_total), 2) AS total
FROM purchase_order po
JOIN res_partner rp ON rp.id = po.partner_id
WHERE po.state IN ('purchase', 'done')
GROUP BY rp.id, 1
ORDER BY total DESC, proveedor
LIMIT 5;

\echo
\echo ===== 4. FACTURAS =====
-- QUE DEMUESTRA: volumen y montos de facturas por tipo y estado, con IVA.
SELECT am.move_type AS tipo, am.state AS estado, count(*) AS documentos,
       round(sum(am.amount_untaxed), 2) AS subtotal, round(sum(am.amount_tax), 2) AS iva,
       round(sum(am.amount_total), 2) AS total
FROM account_move am
WHERE am.move_type IN ('out_invoice', 'in_invoice', 'out_refund', 'in_refund')
GROUP BY am.move_type, am.state
ORDER BY am.move_type, am.state
LIMIT 8;

-- QUE DEMUESTRA: que la suma de lineas iguala el total de cada factura (descuadradas debe ser 0).
SELECT count(*) AS facturas_revisadas,
       count(*) FILTER (WHERE abs(coalesce(l.total, 0) - am.amount_total) > 0.02) AS descuadradas
FROM account_move am
LEFT JOIN (SELECT aml.move_id, sum(aml.price_total) AS total
           FROM account_move_line aml WHERE aml.display_type = 'product' GROUP BY aml.move_id) l
       ON l.move_id = am.id
WHERE am.move_type IN ('out_invoice', 'in_invoice') AND am.state <> 'cancel';

\echo
\echo ===== 5. EMPLEADOS =====
-- QUE DEMUESTRA: la estructura organizacional cruzada (departamento x cargo) de los empleados activos.
SELECT coalesce(to_jsonb(d.name)->>'en_US', to_jsonb(d.name)#>>'{}', '(sin departamento)') AS departamento,
       coalesce(to_jsonb(j.name)->>'en_US', to_jsonb(j.name)#>>'{}', '(sin cargo)')         AS cargo,
       count(*) AS empleados
FROM hr_employee e
LEFT JOIN hr_department d ON d.id = e.department_id
LEFT JOIN hr_job j        ON j.id = e.job_id
WHERE e.active
GROUP BY d.id, j.id, 1, 2
ORDER BY 1, 2
LIMIT 10;

\echo
\echo ===== 6. INTEGRIDAD (todos los hallazgos deben ser 0) =====
-- QUE DEMUESTRA: ausencia de huerfanos, duplicados y descuadres en los controles principales.
SELECT control, hallazgos FROM (
    SELECT 1 AS n, 'venta confirmada sin lineas' AS control, count(*) AS hallazgos
    FROM sale_order so
    WHERE so.state = 'sale'
      AND NOT EXISTS (SELECT 1 FROM sale_order_line sol WHERE sol.order_id = so.id AND sol.display_type IS NULL)
    UNION ALL
    SELECT 2, 'compra confirmada sin lineas', count(*)
    FROM purchase_order po
    WHERE po.state IN ('purchase', 'done')
      AND NOT EXISTS (SELECT 1 FROM purchase_order_line pol WHERE pol.order_id = po.id AND pol.display_type IS NULL)
    UNION ALL
    SELECT 3, 'factura sin lineas de producto', count(*)
    FROM account_move am
    WHERE am.move_type IN ('out_invoice', 'in_invoice') AND am.state <> 'cancel'
      AND NOT EXISTS (SELECT 1 FROM account_move_line aml WHERE aml.move_id = am.id AND aml.display_type = 'product')
    UNION ALL
    SELECT 4, 'factura de proveedor publicada sin orden de compra', count(*)
    FROM account_move am
    WHERE am.move_type = 'in_invoice' AND am.state = 'posted'
      AND NOT EXISTS (SELECT 1 FROM account_move_line aml WHERE aml.move_id = am.id AND aml.purchase_line_id IS NOT NULL)
    UNION ALL
    SELECT 5, 'referencia de cliente duplicada en ventas', count(*)
    FROM (SELECT so.client_order_ref FROM sale_order so
          WHERE so.client_order_ref IS NOT NULL AND so.state <> 'cancel'
          GROUP BY so.client_order_ref HAVING count(*) > 1) d
    UNION ALL
    SELECT 6, 'codigo de producto duplicado', count(*)
    FROM (SELECT pt.default_code FROM product_template pt
          WHERE pt.active AND pt.default_code IS NOT NULL
          GROUP BY pt.default_code HAVING count(*) > 1) d
    UNION ALL
    SELECT 7, 'venta: total distinto de subtotal mas IVA', count(*)
    FROM sale_order so
    WHERE abs(so.amount_total - so.amount_untaxed - so.amount_tax) > 0.02
    UNION ALL
    SELECT 8, 'asiento publicado con debe distinto de haber', count(*)
    FROM (SELECT am.id FROM account_move am
          JOIN account_move_line aml ON aml.move_id = am.id
          WHERE am.state = 'posted'
          GROUP BY am.id HAVING abs(sum(aml.debit) - sum(aml.credit)) > 0.005) d
) controles
ORDER BY n;

\echo
\echo ===== TOTALES DEL INTEGRANTE 1 (prefijo I1-) Y CRITERIO DE CADA CIFRA =====
-- QUE DEMUESTRA: cada cifra del Integrante 1 con el criterio exacto con que se cuenta y su valor verificado ("esperado").
SELECT t.concepto, t.cantidad, t.esperado, t.cantidad = t.esperado AS ok, t.criterio
FROM (
    SELECT 1 AS n, 'Ventas confirmadas' AS concepto, count(*) AS cantidad, 50 AS esperado,
           'sale_order state=sale, client_order_ref I1-V-%' AS criterio
    FROM sale_order so WHERE so.state = 'sale' AND so.client_order_ref LIKE 'I1-V-%'
    UNION ALL
    SELECT 2, '  por facturar', count(*), 33, 'ventas I1-V- con invoice_status=to invoice'
    FROM sale_order so
    WHERE so.state = 'sale' AND so.client_order_ref LIKE 'I1-V-%' AND so.invoice_status = 'to invoice'
    UNION ALL
    SELECT 3, '  facturadas', count(*), 17, 'ventas I1-V- con invoice_status=invoiced'
    FROM sale_order so
    WHERE so.state = 'sale' AND so.client_order_ref LIKE 'I1-V-%' AND so.invoice_status = 'invoiced'
    UNION ALL
    SELECT 4, 'Cotizaciones de venta', count(*), 7, 'sale_order state draft/sent, client_order_ref I1-Q-%'
    FROM sale_order so WHERE so.state IN ('draft', 'sent') AND so.client_order_ref LIKE 'I1-Q-%'
    UNION ALL
    SELECT 5, 'Empleados', count(*), 12, 'hr_employee active, identification_id I1-E-%'
    FROM hr_employee e WHERE e.active AND e.identification_id LIKE 'I1-E-%'
    UNION ALL
    SELECT 6, 'Cargos', count(*), 2, 'hr_job active, nombre exacto (Cajero de Sucursal, Analista de Compras)'
    FROM hr_job j
    WHERE j.active AND coalesce(to_jsonb(j.name)->>'en_US', to_jsonb(j.name)#>>'{}') IN ('Cajero de Sucursal', 'Analista de Compras')
    UNION ALL
    SELECT 7, 'Departamentos', count(*), 2, 'hr_department active, nombre exacto (Operaciones de Tienda, Administracion y Compras)'
    FROM hr_department d
    WHERE d.active AND coalesce(to_jsonb(d.name)->>'en_US', to_jsonb(d.name)#>>'{}') IN ('Operaciones de Tienda', 'Administracion y Compras')
    UNION ALL
    SELECT 8, 'Compras confirmadas', count(*), 33, 'purchase_order state purchase/done, partner_ref I1-OC-%'
    FROM purchase_order po WHERE po.state IN ('purchase', 'done') AND po.partner_ref LIKE 'I1-OC-%'
    UNION ALL
    SELECT 9, 'Materiales', count(*), 20, 'product_template default_code I1-MAT-%'
    FROM product_template pt WHERE pt.default_code LIKE 'I1-MAT-%'
    UNION ALL
    SELECT 10, 'Facturas de proveedor publicadas', count(*), 33, 'account_move in_invoice posted, ref I1-FP-%'
    FROM account_move am WHERE am.move_type = 'in_invoice' AND am.state = 'posted' AND am.ref LIKE 'I1-FP-%'
    UNION ALL
    SELECT 11, 'Facturas de cliente publicadas', count(*), 17, 'account_move out_invoice posted, ref I1-FC-%'
    FROM account_move am WHERE am.move_type = 'out_invoice' AND am.state = 'posted' AND am.ref LIKE 'I1-FC-%'
    UNION ALL
    SELECT 12, 'Documentos de respaldo', count(*), 5, 'ir_attachment name I1-Respaldo-%'
    FROM ir_attachment ia WHERE ia.name LIKE 'I1-Respaldo-%'
) t
ORDER BY t.n;

ROLLBACK;
