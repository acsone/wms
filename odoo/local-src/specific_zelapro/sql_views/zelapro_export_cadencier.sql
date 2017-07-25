CREATE OR REPLACE VIEW zelapro_export_cadencier AS
  SELECT
    info.name AS SFDSUI,
    '' AS SFDNLI,
    product_tmpl.default_code AS SFDART,
    product_tmpl.name AS SFDDEN,
    '' AS SFDQTE,
    '' AS SFDQMO,
    info.price AS SFDPAN,
    '' AS SFDPAM,
    supplier.supplier_discount AS SFDR1O,
    '' AS SFDR1M,
    '' AS SFDR2O, -- TODO When the PR #238 is merged use the field discount_purchase on item
    '' AS SFDR2M,
    to_char(NOW() + format('%s days', COALESCE(info.delay, 0))::INTERVAL, 'DD/MM/YYYY') AS SFEDLI,
    '' AS LIBDLI,
    '' AS SFDDMO,
    '' AS LIBDMO,
    '' AS SFDDBO, -- TODO A se faire expliquer
    '' AS SFDDBM,
    '' AS SFDSTS,
    '' AS SFDTMI, -- TODO Stock minimum total
    '' AS SFDTMA, -- TODO Stock maximum total
    '' AS SFDTST, -- This value will be change in the export
    '' AS SFDTBO,
    '' AS SFDTRE, -- This value will be change in the export
    '' AS SFASUA,
    '' AS SFANLA,
    '' AS SFAQTA,
    '' AS SFASUP,
    '' AS SFANLP,
    '' AS SFAQTP,
    info.create_date AS create_date, -- Mandatory field used to compute data to export
    product_tmpl.id AS product_tmpl_id
  FROM product_supplierinfo AS info
    INNER JOIN product_template AS product_tmpl ON info.product_tmpl_id = product_tmpl.id
    INNER JOIN res_partner AS supplier ON info.name = supplier.id;