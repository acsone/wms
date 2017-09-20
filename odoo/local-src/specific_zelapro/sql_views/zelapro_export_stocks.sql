CREATE OR REPLACE VIEW zelapro_export_stock AS
  SELECT
    '' AS STOSUC,
    '' AS STOLOP,
    product.default_code AS STOREF,
    '' AS STOSTO, -- This value will be computed in the export
    '' AS STORES, -- This value will be computed in the export
    '' AS STODIS, -- This value will be computed in the export
    '' AS STOBOR, -- This value will be computed in the export
    COALESCE(product_tmpl.stock_minimum, 0) AS STOMIN,
    COALESCE(product_tmpl.stock_maximum, 0) AS STOMAX,
    '' AS STOCMO,
    COALESCE(to_char((SELECT move.date
                      FROM stock_move AS move
                        LEFT JOIN stock_location AS loc ON move.location_dest_id = loc.id
                      WHERE move.product_id = product.id
                      AND move.state = 'done'
                      AND loc.kind IN ('reserve', 'bin', 'parking')
                      ORDER BY move.date DESC
                      LIMIT 1), 'DD/MM/YYYY'), '') AS DERNIERE_ENTREE,
    COALESCE(to_char((SELECT move.date
                      FROM stock_move AS move
                        LEFT JOIN stock_location AS loc ON move.location_dest_id = loc.id
                      WHERE move.product_id = product.id
                      AND move.state = 'done'
                      AND loc.usage = 'customer'
                      ORDER BY move.date DESC
                      LIMIT 1), 'DD/MM/YYYY'), '') AS DERNIERE_SORTIE,
    COALESCE(to_char((SELECT move.date
                      FROM stock_move AS move
                        LEFT JOIN stock_location AS loc ON move.location_dest_id = loc.id
                      WHERE move.product_id = product.id
                      AND move.state IN ('assigned', 'confirmed', 'waiting')
                      AND loc.usage = 'customer'
                      ORDER BY move.date
                      LIMIT 1), 'DD/MM/YYYY'), '') AS PLUS_ANCIEN_BO,
    '' AS STOCDE,
    product.id AS product_id,
    product.create_date AS create_date -- Mandatory field used to compute data to export
  FROM product_product AS product
    INNER JOIN product_template AS product_tmpl ON product.product_tmpl_id = product_tmpl.id
  WHERE product.active = TRUE;