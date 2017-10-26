CREATE OR REPLACE VIEW zelapro_export_lots AS
  SELECT
    1 AS LOTSUC,
    product.default_code AS LOTREF,
    lot.name AS LOTNUM,
    SUM(quant.qty) AS LOTACT,
    to_char(lot.life_date, 'DD/MM/YYYY') AS DATE_PEREMPTION,
    lot.create_date AS create_date -- Mandatory field used to compute data to export
  FROM stock_quant AS quant
    INNER JOIN stock_production_lot AS lot ON quant.lot_id = lot.id
    INNER JOIN product_product AS product ON quant.product_id = product.id
    INNER JOIN stock_location AS location ON quant.location_id = location.id
  WHERE lot.is_archived = FALSE
    AND location.usage = 'internal'
  GROUP BY lot.id, product.default_code;