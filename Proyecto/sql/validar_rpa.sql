-- Ejecutar en PostgreSQL con el rol de solo lectura, después de una carga real.
-- Cambia el prefijo por las referencias usadas en la demostración.
SELECT id, name, ref, email, company_type
FROM res_partner
WHERE ref LIKE 'RPA-PRUEBA-%'
ORDER BY id;

SELECT pt.id AS producto_id,
       pt.x_rpa_external_id,
       pt.x_rpa_product_values,
       pp.id AS variante_id,
       pp.default_code AS referencia_interna,
       COALESCE(SUM(CASE WHEN sw.id IS NOT NULL THEN sq.quantity ELSE 0 END), 0) AS cantidad_wh_stock
FROM product_template AS pt
JOIN product_product AS pp ON pp.product_tmpl_id = pt.id
LEFT JOIN stock_quant AS sq ON sq.product_id = pp.id
LEFT JOIN stock_location AS sl ON sl.id = sq.location_id
LEFT JOIN stock_warehouse AS sw ON sw.lot_stock_id = sl.id AND sw.code = 'WH'
WHERE pt.x_rpa_external_id LIKE 'RPA-PRUEBA-%'
GROUP BY pt.id, pt.x_rpa_external_id, pt.x_rpa_product_values, pp.id, pp.default_code
ORDER BY pt.id, pp.id;
