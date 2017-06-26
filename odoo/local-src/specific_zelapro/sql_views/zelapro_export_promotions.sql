CREATE OR REPLACE VIEW zelapro_export_promotions AS
  SELECT
    ''                   AS CODE_REMISE,
    product.default_code AS ARTICLE,
    item.date_start      AS DATE_DEBUT,
    item.date_end        AS DATE_FIN,
    item.percent_price   AS POURCENTAGE_1,
    ''                   AS POURCENTAGE_2,
    item.min_quantity    AS QUANTITE,
    ''                   AS GRATUIT
  FROM product_pricelist_item AS item
    INNER JOIN product_product AS product ON item.product_id = product.id
  WHERE item.pricelist_id =
        (SELECT imd.res_id
         FROM ir_model_data AS imd
         WHERE module = '__setup__'
AND NAME = 'product_pricelist_supplier')
AND item.date_end >= NOW() - INTERVAL '2 YEARS ';