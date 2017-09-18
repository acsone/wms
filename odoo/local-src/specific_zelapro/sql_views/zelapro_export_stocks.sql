CREATE OR REPLACE VIEW zelapro_export_stock AS
  SELECT
    '' AS STOSUC,
    '' AS STOLOP,
    product.default_code AS STOREF,
    '' AS STOSTO,
    '' AS STORES,
    '' AS STODIS,
    '' AS STOBOR,
    product_tmpl.stock_minimum AS STOMIN,
    product_tmpl.stock_maximum AS STOMAX,
    '' AS STOCMO,
    '' AS DERNIERE_ENTREE,
    '' AS DERNIERE_SORTIE,
    '' AS PLUS_ANCIEN_BO,
    '' AS STOCDE,
    product.id AS product_id,
    product.create_date AS create_date -- Mandatory field used to compute data to export
  FROM product_product AS product
    INNER JOIN product_template AS product_tmpl ON product.product_tmpl_id = product_tmpl.id