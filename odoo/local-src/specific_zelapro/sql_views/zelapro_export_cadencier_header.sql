CREATE OR REPLACE VIEW zelapro_export_cadencier_header AS
  SELECT
    supplier.id AS SFESUI,
    supplier.ref AS SFEFOU,
    supplier.name AS SFENFO,
    to_char(NOW() + format('%s days', COALESCE(delivery_lead_time, 0))::INTERVAL, 'DD/MM/YYYY') AS SFEDLI,
    '' AS LIBDLI,
    '' AS SFEPDS,
    '' AS SFEMNT,
    '' AS SFEMNS,
    (SELECT min(stock_move.create_date) AS older_bo
     FROM stock_move
       INNER JOIN product_product ON stock_move.product_id = product_product.id
     WHERE stock_move.state NOT IN ('cancel', 'done')
      AND product_product.product_tmpl_id IN (
       SELECT DISTINCT supplierinfo.product_tmpl_id
       FROM product_supplierinfo AS supplierinfo
       WHERE supplierinfo.name = supplier.id
      )
    ) AS SFEDBO,
    '' AS LIBDBO,
    '' AS SFESTS,
    supplier.create_date AS create_date -- Mandatory field used to compute data to export
  FROM res_partner AS supplier
  WHERE supplier.supplier = TRUE;
