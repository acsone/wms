CREATE OR REPLACE VIEW zelapro_export_promotions AS
  SELECT
    ''                         AS CODE_REMISE,
    product.default_code       AS ARTICLE,
    item.date_start            AS DATE_DEBUT,
    item.date_end              AS DATE_FIN,
    supplier.supplier_discount AS POURCENTAGE_1,
    ''                         AS POURCENTAGE_2, -- When the PR #238 is merged use the field discount_purchase on item
    item.min_qty               AS QUANTITE,
    ''                         AS GRATUIT,
    item.create_date           AS create_date
  FROM product_supplierinfo AS item
    INNER JOIN product_product AS product ON item.product_id = product.id
    INNER JOIN res_partner AS supplier ON item.name = supplier.id;
