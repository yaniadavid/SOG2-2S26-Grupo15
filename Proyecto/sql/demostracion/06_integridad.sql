\echo
\echo ===== 06. INTEGRIDAD (si todo esta sano devuelve 0 filas) =====
-- QUE DEMUESTRA: ausencia de huerfanos, duplicados y descuadres. Cada fila es un hallazgo.
-- Tolerancia de montos: 0.02 por redondeo de impuestos.
SELECT control, referencia, detalle FROM (

    -- Huerfanos: documentos sin lineas
    SELECT 'orden de venta confirmada sin lineas' AS control, so.name AS referencia, so.state AS detalle
    FROM sale_order so
    WHERE so.state = 'sale'
      AND NOT EXISTS (SELECT 1 FROM sale_order_line sol WHERE sol.order_id = so.id AND sol.display_type IS NULL)
    UNION ALL
    SELECT 'orden de compra confirmada sin lineas', po.name, po.state
    FROM purchase_order po
    WHERE po.state IN ('purchase', 'done')
      AND NOT EXISTS (SELECT 1 FROM purchase_order_line pol WHERE pol.order_id = po.id AND pol.display_type IS NULL)
    UNION ALL
    SELECT 'factura sin lineas de producto', am.name, am.move_type
    FROM account_move am
    WHERE am.move_type IN ('out_invoice', 'in_invoice') AND am.state <> 'cancel'
      AND NOT EXISTS (SELECT 1 FROM account_move_line aml WHERE aml.move_id = am.id AND aml.display_type = 'product')
    UNION ALL

    -- Huerfanos: documentos o personas sin relaciones obligatorias
    SELECT 'orden de venta sin cliente', so.name, so.state
    FROM sale_order so WHERE so.partner_id IS NULL
    UNION ALL
    SELECT 'orden de compra sin proveedor', po.name, po.state
    FROM purchase_order po WHERE po.partner_id IS NULL
    UNION ALL
    SELECT 'factura sin tercero', am.name, am.move_type
    FROM account_move am
    WHERE am.move_type IN ('out_invoice', 'in_invoice') AND am.partner_id IS NULL
    UNION ALL
    SELECT 'empleado activo sin cargo o departamento', e.name,
           CASE WHEN e.job_id IS NULL THEN 'sin cargo' ELSE 'sin departamento' END
    FROM hr_employee e
    WHERE e.active AND (e.job_id IS NULL OR e.department_id IS NULL)
    UNION ALL
    SELECT 'cargo activo sin empleados', coalesce(to_jsonb(j.name)->>'en_US', to_jsonb(j.name)#>>'{}'), 'sin empleados activos'
    FROM hr_job j
    WHERE j.active AND NOT EXISTS (SELECT 1 FROM hr_employee e WHERE e.job_id = j.id AND e.active)
    UNION ALL
    SELECT 'departamento activo sin empleados', coalesce(to_jsonb(d.name)->>'en_US', to_jsonb(d.name)#>>'{}'), 'sin empleados activos'
    FROM hr_department d
    WHERE d.active AND NOT EXISTS (SELECT 1 FROM hr_employee e WHERE e.department_id = d.id AND e.active)
    UNION ALL
    SELECT 'factura de proveedor publicada sin orden de compra', am.name, coalesce(am.ref, '')
    FROM account_move am
    WHERE am.move_type = 'in_invoice' AND am.state = 'posted'
      AND NOT EXISTS (
          SELECT 1 FROM account_move_line aml
          WHERE aml.move_id = am.id AND aml.purchase_line_id IS NOT NULL)
    UNION ALL

    -- Duplicados
    SELECT 'numero de orden de venta duplicado', so.name, count(*)::text
    FROM sale_order so GROUP BY so.name, so.company_id HAVING count(*) > 1
    UNION ALL
    SELECT 'numero de orden de compra duplicado', po.name, count(*)::text
    FROM purchase_order po GROUP BY po.name, po.company_id HAVING count(*) > 1
    UNION ALL
    SELECT 'numero de factura publicada duplicado', am.name, count(*)::text
    FROM account_move am
    WHERE am.state = 'posted' AND am.move_type IN ('out_invoice', 'in_invoice')
    GROUP BY am.name, am.journal_id HAVING count(*) > 1
    UNION ALL
    SELECT 'referencia de cliente duplicada en ventas', so.client_order_ref, count(*)::text
    FROM sale_order so
    WHERE so.client_order_ref IS NOT NULL AND so.state <> 'cancel'
    GROUP BY so.client_order_ref HAVING count(*) > 1
    UNION ALL
    SELECT 'codigo de producto duplicado', pt.default_code, count(*)::text
    FROM product_template pt
    WHERE pt.active AND pt.default_code IS NOT NULL
    GROUP BY pt.default_code HAVING count(*) > 1
    UNION ALL
    SELECT 'empleado activo duplicado por nombre', e.name, count(*)::text
    FROM hr_employee e WHERE e.active
    GROUP BY e.name, e.company_id HAVING count(*) > 1
    UNION ALL

    -- Descuadres: encabezado contra suma de lineas
    SELECT 'venta: total distinto de la suma de lineas', so.name,
           so.amount_total::text || ' vs ' || coalesce(l.total, 0)::text
    FROM sale_order so
    LEFT JOIN (SELECT sol.order_id, sum(sol.price_total) AS total
               FROM sale_order_line sol WHERE sol.display_type IS NULL GROUP BY sol.order_id) l
           ON l.order_id = so.id
    WHERE so.state <> 'cancel' AND abs(so.amount_total - coalesce(l.total, 0)) > 0.02
    UNION ALL
    SELECT 'compra: total distinto de la suma de lineas', po.name,
           po.amount_total::text || ' vs ' || coalesce(l.total, 0)::text
    FROM purchase_order po
    LEFT JOIN (SELECT pol.order_id, sum(pol.price_total) AS total
               FROM purchase_order_line pol WHERE pol.display_type IS NULL GROUP BY pol.order_id) l
           ON l.order_id = po.id
    WHERE po.state <> 'cancel' AND abs(po.amount_total - coalesce(l.total, 0)) > 0.02
    UNION ALL
    SELECT 'factura: total distinto de la suma de lineas', am.name,
           am.amount_total::text || ' vs ' || coalesce(l.total, 0)::text
    FROM account_move am
    LEFT JOIN (SELECT aml.move_id, sum(aml.price_total) AS total
               FROM account_move_line aml WHERE aml.display_type = 'product' GROUP BY aml.move_id) l
           ON l.move_id = am.id
    WHERE am.move_type IN ('out_invoice', 'in_invoice') AND am.state <> 'cancel'
      AND abs(am.amount_total - coalesce(l.total, 0)) > 0.02
    UNION ALL
    SELECT 'total distinto de subtotal mas IVA (venta)', so.name, so.amount_total::text
    FROM sale_order so
    WHERE abs(so.amount_total - so.amount_untaxed - so.amount_tax) > 0.02
    UNION ALL
    SELECT 'total distinto de subtotal mas IVA (compra)', po.name, po.amount_total::text
    FROM purchase_order po
    WHERE abs(po.amount_total - po.amount_untaxed - po.amount_tax) > 0.02
    UNION ALL
    SELECT 'total distinto de subtotal mas IVA (factura)', am.name, am.amount_total::text
    FROM account_move am
    WHERE am.move_type IN ('out_invoice', 'in_invoice')
      AND abs(am.amount_total - am.amount_untaxed - am.amount_tax) > 0.02
    UNION ALL
    SELECT 'asiento publicado con debe distinto de haber', am.name,
           sum(aml.debit)::text || ' vs ' || sum(aml.credit)::text
    FROM account_move am
    JOIN account_move_line aml ON aml.move_id = am.id
    WHERE am.state = 'posted'
    GROUP BY am.id HAVING abs(sum(aml.debit) - sum(aml.credit)) > 0.005
    UNION ALL
    SELECT 'documento en moneda distinta de GTQ', x.nombre, x.moneda
    FROM (
        SELECT so.name AS nombre, rc.name::text AS moneda
        FROM sale_order so JOIN res_currency rc ON rc.id = so.currency_id
        UNION ALL
        SELECT po.name, rc.name::text
        FROM purchase_order po JOIN res_currency rc ON rc.id = po.currency_id
        UNION ALL
        SELECT am.name, rc.name::text
        FROM account_move am JOIN res_currency rc ON rc.id = am.currency_id
        WHERE am.move_type IN ('out_invoice', 'in_invoice')
    ) x
    WHERE x.moneda <> 'GTQ'
) hallazgos
ORDER BY control, referencia;
