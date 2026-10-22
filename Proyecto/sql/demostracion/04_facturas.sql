\echo
\echo ===== 04. FACTURAS =====

\echo
\echo --- 04.1 Facturas por tipo y estado
-- QUE DEMUESTRA: volumen y montos de facturas de cliente y proveedor (y notas de credito) en cada estado.
SELECT am.move_type                     AS tipo,
       am.state                         AS estado,
       count(*)                         AS documentos,
       round(sum(am.amount_untaxed), 2) AS subtotal,
       round(sum(am.amount_tax), 2)     AS iva,
       round(sum(am.amount_total), 2)   AS total
FROM account_move am
WHERE am.move_type IN ('out_invoice', 'in_invoice', 'out_refund', 'in_refund')
GROUP BY am.move_type, am.state
ORDER BY am.move_type, am.state;

\echo
\echo --- 04.2 Estado de pago de las facturas publicadas
-- QUE DEMUESTRA: cuanto de lo facturado esta pagado, parcial o pendiente.
SELECT am.move_type                      AS tipo,
       am.payment_state                  AS pago,
       count(*)                          AS documentos,
       round(sum(am.amount_total), 2)    AS total,
       round(sum(am.amount_residual), 2) AS saldo_pendiente
FROM account_move am
WHERE am.move_type IN ('out_invoice', 'in_invoice') AND am.state = 'posted'
GROUP BY am.move_type, am.payment_state
ORDER BY am.move_type, am.payment_state;

\echo
\echo --- 04.3 Tasa efectiva de IVA en facturas publicadas
-- QUE DEMUESTRA: que el IVA aplicado equivale al 12 % del subtotal.
SELECT am.move_type                     AS tipo,
       round(sum(am.amount_untaxed), 2) AS subtotal,
       round(sum(am.amount_tax), 2)     AS iva,
       round(100 * sum(am.amount_tax) / nullif(sum(am.amount_untaxed), 0), 2) AS iva_pct
FROM account_move am
WHERE am.move_type IN ('out_invoice', 'in_invoice') AND am.state = 'posted'
GROUP BY am.move_type
ORDER BY am.move_type;

\echo
\echo --- 04.4 Cuadre de lineas contra encabezado (facturas de cliente y proveedor)
-- QUE DEMUESTRA: que la suma de lineas de producto iguala amount_untaxed y amount_total de cada factura;
-- "descuadradas" debe ser 0 (tolerancia 0.02 por redondeo).
WITH sumas AS (
    SELECT am.id, am.amount_untaxed, am.amount_total,
           coalesce(sum(aml.price_subtotal), 0) AS lineas_subtotal,
           coalesce(sum(aml.price_total), 0)    AS lineas_total
    FROM account_move am
    LEFT JOIN account_move_line aml ON aml.move_id = am.id AND aml.display_type = 'product'
    WHERE am.move_type IN ('out_invoice', 'in_invoice') AND am.state <> 'cancel'
    GROUP BY am.id
)
SELECT count(*) AS facturas_revisadas,
       count(*) FILTER (WHERE abs(s.lineas_subtotal - s.amount_untaxed) > 0.02
                           OR abs(s.lineas_total - s.amount_total) > 0.02) AS descuadradas,
       round(sum(s.lineas_total), 2) AS suma_lineas_total,
       round(sum(s.amount_total), 2) AS suma_amount_total
FROM sumas s;
