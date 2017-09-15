CREATE OR REPLACE VIEW zelapro_export_promotions AS
  SELECT
    ''                                                  AS CODE_REMISE,
    product_tmpl.default_code                           AS ARTICLE,
    COALESCE(to_char(item.date_start, 'DD-Mon-YY'), '') AS DATE_DEBUT,
    COALESCE(to_char(item.date_end, 'DD-Mon-YY'), '')   AS DATE_FIN,
    COALESCE(supplier.supplier_discount, 0)             AS POURCENTAGE_1,
    COALESCE(item.discount_purchase, 0)                 AS POURCENTAGE_2,
    COALESCE(item.min_qty, 0)                           AS QUANTITE,
    ''                                                  AS GRATUIT,
    item.create_date                                    AS create_date -- Mandatory field used to compute data to export
  FROM product_supplierinfo AS item
    INNER JOIN product_template AS product_tmpl
      ON item.product_tmpl_id = product_tmpl.id
    INNER JOIN res_partner AS supplier ON item.name = supplier.id
  WHERE product_tmpl.active = TRUE;
