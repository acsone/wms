CREATE OR REPLACE VIEW zelapro_export_stock AS
  SELECT
    '' AS STOSUC,
    '' AS STOLOP,
    product.default_code AS STOREF,
    '' AS STOSTO, -- This value will be computed in the export
    '' AS STORES, -- This value will be computed in the export
    '' AS STODIS, -- This value will be computed in the export
    '' AS STOBOR,
    COALESCE(product_tmpl.stock_minimum, 0) AS STOMIN,
    COALESCE(product_tmpl.stock_maximum, 0) AS STOMAX,
    '' AS STOCMO,
    COALESCE(to_char((SELECT max(in_date) FROM stock_quant WHERE product_id = product.id AND qty > 0), 'DD/MM/YYYY'), '') AS DERNIERE_ENTREE,
    COALESCE(to_char((SELECT max(in_date) FROM stock_quant WHERE product_id = product.id AND qty < 0), 'DD/MM/YYYY'), '') AS DERNIERE_SORTIE,
    '' AS PLUS_ANCIEN_BO,
    '' AS STOCDE,
    product.id AS product_id,
    product.create_date AS create_date -- Mandatory field used to compute data to export
  FROM product_product AS product
    INNER JOIN product_template AS product_tmpl ON product.product_tmpl_id = product_tmpl.id