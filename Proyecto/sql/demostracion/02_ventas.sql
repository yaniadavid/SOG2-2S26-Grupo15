\echo
\echo ===== 02. VENTAS =====

\echo
\echo --- 02.1 Ventas confirmadas por mes (GTQ)
-- QUE DEMUESTRA: la distribucion temporal de las ordenes confirmadas y sus montos sin IVA, IVA y total.
SELECT to_char(date_trunc('month', so.date_order), 'YYYY-MM') AS mes,
       count(*)                         AS ordenes,
       round(sum(so.amount_untaxed), 2) AS subtotal,
       round(sum(so.amount_tax), 2)     AS iva,
       round(sum(so.amount_total), 2)   AS total
FROM sale_order so
WHERE so.state = 'sale'
GROUP BY 1
ORDER BY 1;

\echo
\echo --- 02.2 Ventas confirmadas por cliente (top 15 por monto)
-- QUE DEMUESTRA: que las ventas estan asociadas a clientes reales y cuanto compra cada uno.
SELECT coalesce(to_jsonb(rp.name)->>'en_US', to_jsonb(rp.name)#>>'{}') AS cliente,
       count(*)                       AS ordenes,
       round(sum(so.amount_total), 2) AS total
FROM sale_order so
JOIN res_partner rp ON rp.id = so.partner_id
WHERE so.state = 'sale'
GROUP BY rp.id, 1
ORDER BY total DESC, cliente
LIMIT 15;

\echo
\echo --- 02.3 Top 10 productos vendidos
-- QUE DEMUESTRA: los productos mas vendidos por unidades y su ingreso (lineas de producto de ventas confirmadas).
SELECT coalesce(to_jsonb(pt.name)->>'en_US', to_jsonb(pt.name)#>>'{}') AS producto,
       pt.default_code                   AS codigo,
       sum(sol.product_uom_qty)          AS unidades,
       round(sum(sol.price_subtotal), 2) AS ingreso_sin_iva
FROM sale_order_line sol
JOIN sale_order so       ON so.id = sol.order_id
JOIN product_product pp  ON pp.id = sol.product_id
JOIN product_template pt ON pt.id = pp.product_tmpl_id
WHERE so.state = 'sale' AND sol.display_type IS NULL
GROUP BY pt.id, 1, 2
ORDER BY unidades DESC, producto
LIMIT 10;

\echo
\echo --- 02.4 Cotizaciones versus ventas confirmadas
-- QUE DEMUESTRA: el embudo comercial; cada estado de sale.order con su cantidad y monto.
SELECT CASE so.state
           WHEN 'draft'  THEN 'Cotizacion (borrador)'
           WHEN 'sent'   THEN 'Cotizacion enviada'
           WHEN 'sale'   THEN 'Venta confirmada'
           WHEN 'cancel' THEN 'Cancelada'
       END AS estado,
       count(*)                       AS ordenes,
       round(sum(so.amount_total), 2) AS total
FROM sale_order so
GROUP BY so.state
ORDER BY so.state;
