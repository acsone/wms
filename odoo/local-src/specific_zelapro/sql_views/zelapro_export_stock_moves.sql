CREATE OR REPLACE VIEW zelapro_export_stock_moves AS
  SELECT
    1 AS MVTSUC,
    '' AS MVTSSU,
    '' AS MVTCTR,
    move.origin AS MVTNCD,
    to_char(move.create_date, 'DD/MM/YYYY') AS DATE_MOUVEMENT,
    partner.ref AS MVTNIM,
    product.default_code AS MVTREF,
    CASE
      WHEN picking_type.code = 'outgoing' THEN ('-' || move.product_uom_qty)::NUMERIC
      ELSE move.product_uom_qty
    END AS MVTQUC,
    move.create_date AS create_date
  FROM stock_move AS move
    LEFT JOIN stock_picking AS picking ON move.picking_id = picking.id
    LEFT JOIN stock_picking_type AS picking_type ON move.picking_type_id = picking_type.id
    LEFT JOIN res_partner AS partner ON move.partner_id = partner.id
    LEFT JOIN product_product AS product ON move.product_id = product.id
  WHERE (picking.name LIKE 'WH/OUT/%' OR picking.name LIKE 'WH/IN/%s')
  AND move.state = 'done'
  AND (move.origin LIKE 'SO%' OR move.origin LIKE 'PO%');
