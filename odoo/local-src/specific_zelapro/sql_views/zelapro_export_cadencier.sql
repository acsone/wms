CREATE OR REPLACE VIEW zelapro_export_cadencier AS
  SELECT
    info.name AS SFDSUI,
    '' AS SFDNLI, -- This value will be computed in the export
    product_tmpl.default_code AS SFDART,
    product_tmpl.name AS SFDDEN,
    '' AS SFDQTE,
    '' AS SFDQMO,
    info.price AS SFDPAN,
    '' AS SFDPAM,
    supplier.supplier_discount AS SFDR1O,
    '' AS SFDR1M,
    info.discount_purchase AS SFDR2O,
    '' AS SFDR2M,
    to_char(NOW() + format('%s days', COALESCE(info.delay, 0))::INTERVAL, 'DD/MM/YYYY') AS SFEDLI,
    '' AS LIBDLI,
    '' AS SFDDMO,
    '' AS LIBDMO,
    CASE
      WHEN supplier.is_back_order_accepted = TRUE THEN 1
      ELSE 0
    END AS SFDDBO,
    '' AS SFDDBM,
    '' AS SFDSTS,
    product_tmpl.stock_minimum AS SFDTMI,
    product_tmpl.stock_maximum AS SFDTMA,
    '' AS SFDTST, -- This value will be computed in the export
    '' AS SFDTBO, -- This value will be computed in the export
    '' AS SFDTRE, -- This value will be computed in the export
    '' AS SFASUA, -- This value will be computed in the export
    '' AS SFANLA, -- This value will be computed in the export
    '' AS SFAQTA,
    '' AS SFASUP, -- This value will be computed in the export
    '' AS SFANLP, -- This value will be computed in the export
    '' AS SFAQTP,
    product_tmpl.id AS product_tmpl_id,
    info.create_date AS create_date -- Mandatory field used to compute data to export
  FROM product_supplierinfo AS info
    INNER JOIN product_template AS product_tmpl ON info.product_tmpl_id = product_tmpl.id
    INNER JOIN res_partner AS supplier ON info.name = supplier.id
  ORDER BY info.name, product_tmpl.default_code;