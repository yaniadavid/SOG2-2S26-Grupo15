\echo
\echo ===== 03. COMPRAS =====

\echo
\echo --- 03.1 Compras confirmadas por proveedor
-- QUE DEMUESTRA: cuantas ordenes de compra confirmadas tiene cada proveedor y su monto total.
SELECT coalesce(to_jsonb(rp.name)->>'en_US', to_jsonb(rp.name)#>>'{}') AS proveedor,
       count(*)                       AS ordenes,
       round(sum(po.amount_total), 2) AS total
FROM purchase_order po
JOIN res_partner rp ON rp.id = po.partner_id
WHERE po.state IN ('purchase', 'done')
GROUP BY rp.id, 1
ORDER BY total DESC, proveedor;

\echo
\echo --- 03.2 Compras por material (top 20)
-- QUE DEMUESTRA: que materiales se compran, en que cantidad y a que costo (sin IVA).
SELECT coalesce(to_jsonb(pt.name)->>'en_US', to_jsonb(pt.name)#>>'{}') AS material,
       pt.default_code                   AS codigo,
       sum(pol.product_qty)              AS cantidad,
       round(sum(pol.price_subtotal), 2) AS costo_sin_iva
FROM purchase_order_line pol
JOIN purchase_order po   ON po.id = pol.order_id
JOIN product_product pp  ON pp.id = pol.product_id
JOIN product_template pt ON pt.id = pp.product_tmpl_id
WHERE po.state IN ('purchase', 'done') AND pol.display_type IS NULL
GROUP BY pt.id, 1, 2
ORDER BY costo_sin_iva DESC, material
LIMIT 20;

\echo
\echo --- 03.3 Orden de compra y su factura de proveedor vinculada
-- QUE DEMUESTRA: el vinculo compra -> factura (via purchase_line_id) con estado y monto de cada factura.
SELECT po.name                    AS orden_compra,
       po.state                   AS estado_oc,
       coalesce(to_jsonb(rp.name)->>'en_US', to_jsonb(rp.name)#>>'{}') AS proveedor,
       round(po.amount_total, 2)  AS total_oc,
       am.name                    AS factura,
       am.state                   AS estado_factura,
       am.payment_state           AS pago,
       round(am.amount_total, 2)  AS total_factura
FROM purchase_order po
JOIN res_partner rp          ON rp.id = po.partner_id
JOIN purchase_order_line pol ON pol.order_id = po.id
JOIN account_move_line aml   ON aml.purchase_line_id = pol.id
JOIN account_move am         ON am.id = aml.move_id AND am.move_type = 'in_invoice'
WHERE po.state IN ('purchase', 'done')
GROUP BY po.id, rp.id, am.id
ORDER BY po.name, am.name;

\echo
\echo --- 03.4 Resumen de compras confirmadas con y sin factura de proveedor
-- QUE DEMUESTRA: cuantas compras confirmadas ya tienen factura de proveedor y cuantas faltan.
SELECT count(*) AS compras_confirmadas,
       count(*) FILTER (WHERE EXISTS (
           SELECT 1
           FROM purchase_order_line pol
           JOIN account_move_line aml ON aml.purchase_line_id = pol.id
           JOIN account_move am       ON am.id = aml.move_id
           WHERE pol.order_id = po.id AND am.move_type = 'in_invoice' AND am.state <> 'cancel'
       )) AS con_factura,
       count(*) FILTER (WHERE NOT EXISTS (
           SELECT 1
           FROM purchase_order_line pol
           JOIN account_move_line aml ON aml.purchase_line_id = pol.id
           JOIN account_move am       ON am.id = aml.move_id
           WHERE pol.order_id = po.id AND am.move_type = 'in_invoice' AND am.state <> 'cancel'
       )) AS sin_factura
FROM purchase_order po
WHERE po.state IN ('purchase', 'done');
