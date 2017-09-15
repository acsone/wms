CREATE OR REPLACE VIEW zelapro_export_lot_moves AS
  SELECT
    '' AS ROW,
    1 AS DEPOT,
    '' AS SOUS_DEPOT,
    '' AS CODE_TRAVAIL,
    move.origin AS COMMANDE,
    to_char(move.date, 'DD/MM/YYYY') AS DATE_MOUVEMENT,
    product.default_code AS ARTICLE,
    quant.qty AS QUANTITE,
    lot.name AS LOT,
    to_char(lot.life_date, 'DD/MM/YYYY') AS DATE_PEREMPTION,
    move.create_date AS create_date -- Mandatory field used to compute data to export
  FROM stock_quant_move_rel AS rel
    INNER JOIN stock_move AS move ON rel.move_id = move.id
    INNER JOIN stock_picking AS picking ON move.picking_id = picking.id
    INNER JOIN stock_quant AS quant ON rel.quant_id = quant.id
    INNER JOIN stock_production_lot AS lot ON quant.lot_id = lot.id
    INNER JOIN product_product AS product ON move.product_id = product.id
  WHERE (picking.name LIKE 'WH/OUT/%' OR picking.name LIKE 'WH/IN/%s')
  AND move.state = 'done'
  AND (move.origin LIKE 'SO%' OR move.origin LIKE 'PO%');