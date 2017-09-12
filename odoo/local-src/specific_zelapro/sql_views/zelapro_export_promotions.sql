CREATE OR REPLACE VIEW zelapro_export_promotions AS
  SELECT
    ''                         AS CODE_REMISE,
    product_tmpl.default_code  AS ARTICLE,
    item.date_start            AS DATE_DEBUT,
    item.date_end              AS DATE_FIN,
    supplier.supplier_discount AS POURCENTAGE_1,
    item.discount_purchase     AS POURCENTAGE_2,
    item.min_qty               AS QUANTITE,
    ''                         AS GRATUIT,
    item.create_date           AS create_date -- Mandatory field used to compute data to export
  FROM product_supplierinfo AS item
    INNER JOIN product_template AS product_tmpl ON item.product_tmpl_id = product_tmpl.id
    INNER JOIN res_partner AS supplier ON item.name = supplier.id;
