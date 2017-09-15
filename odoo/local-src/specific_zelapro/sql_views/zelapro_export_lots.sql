CREATE OR REPLACE VIEW zelapro_export_lots AS
  SELECT
    1 AS LOTSUC,
    product.default_code AS LOTREF,
    lot.name AS LOTNUM,
    '' AS LOTACT,
    to_char(lot.life_date, 'DD/MM/YYYY') AS DATE_PEREMPTION,
    lot.id AS lot_id,
    lot.create_date AS create_date -- Mandatory field used to compute data to export
  FROM stock_production_lot AS lot
    INNER JOIN product_product AS product ON lot.product_id = product.id
  WHERE lot.is_archived = FALSE;