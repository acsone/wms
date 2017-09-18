CREATE OR REPLACE VIEW zelapro_export_products AS
  SELECT
    COALESCE(product.default_code, '') AS GESART,
    product_tmpl.name AS GESDEM,
    COALESCE(product.weight, 0) AS GESPBR,
    '' AS GESPNT,
    '' AS GESVOL,
    COALESCE(supplier.ref, '') AS GESFOU,
    '' AS GESCDE,
    '' AS LIBCDE,
    '' AS GESDOU,
    '' AS GESCRF,
    '' AS GESUNA,
    COALESCE(purchase_uom.name, '') AS LIBUNA,
    1  AS GESCOA, -- A vérifier => Pas toujours 1
    '' AS GESNBP,
    COALESCE(supplierinfo.delay, 0) AS GESDEL, -- Problème avec les valeurs
    '' AS GESECS,
    '' AS GESBPV,
    '' AS GESUNV,
    COALESCE(sale_uom.name, '') AS LIBUNV,
    1 AS GESCOV,
    '' AS GESCGE,
    '' AS LIBCGE,
    '' AS GESHIS,
    '' AS LIBHIS,
    '' AS GESMCO,
    '' AS LIBCMO,
    '' AS GESETI,
    '' AS LIBETI,
    '' AS GESCGR,
    COALESCE(product_category.name, '') AS LIBCGR,
    '' AS GESCSG,
    COALESCE(product_sub_category.name, '') AS LIBCSG,
    '' AS GESCTV,
    '' AS LIBCTV,
    '' AS GESCVA,
    '' AS GESCVV,
    '' AS GESCAN,
    '' AS GESCAV,
    '' AS GESCSA,
    CASE
      WHEN product_tmpl.tracking = 'lot' THEN 'Suivi en lot'
      ELSE 'Pas de suivi'
    END AS LIBCSA,
    '' AS GESCRE,
    '' AS LIBCRE,
    '' AS GESCHR,
    state.name AS LIBCHR, -- Pas alimenter par Odoo
    COALESCE((SELECT ir_property.value_float
     FROM ir_property
     WHERE ir_property.res_id = 'product.product,' || product.id), 0) AS GESPAB, -- N'est pas récupéré. A vérifier !!!!!
    COALESCE(supplierinfo.price, 0) AS GESPAN,
    '' AS GESPRR,
    COALESCE(product_tmpl.list_price, 0) AS GESPVR,
    '' AS GESPRM,
    '' AS GESPMC,
    to_char(product.create_date, 'DD/MM/YYYY') AS DATE_CREATION,
    to_char(product.write_date, 'DD/MM/YYYY') AS DATE_MODIFICATION,
    '' AS GESSOC,
    '' AS GESARC,
    '' AS GESPV2,
    '' AS GESDON,
    '' AS GESSUR,
    '' AS GESSUN,
    '' AS GESSUP,
    '' AS CPLZ03,
    '' AS CPLZ13,
    '' AS LIBZ13,
    '' AS CPLZ14,
    '' AS LIBZ14,
    '' AS CPLZ25,
    '' AS CPLZ20,
    '' AS CPLZ21,
    '' AS CPLZ24,
    '' AS CPLZ29,
    COALESCE(product_tmpl.unit_in_box, 0) AS CPLZ30, -- A importer
    '' AS CPLZ18,
    '' AS CPLZ19,
    '' AS CPLZ22,
    '' AS CPLZ23,
    '' AS CPLZ28,
    '' AS CP2Z01,
    COALESCE(product_tmpl.unit_in_shrink_wrap, 0) AS CP2Z02,
    '' AS CP2Z03,
    COALESCE(product_tmpl.unit_in_box, 0) AS CP2Z04, -- A importer
    '' AS CP2Z05,
    '' AS CP2Z06,
    '' AS CP2Z08,
    '' AS CP2Z09,
    '' AS CP2Z10,
    '' AS CP2Z11,
    '' AS CP2Z12,
    '' AS CP2Z13,
    '' AS CP2Z14,
    '' AS CP2Z15,
    '' AS CP2Z16,
    '' AS CP2Z17,
    '' AS LIBZ17,
    '' AS CP2Z18,
    '' AS LIBZ18,
    '' AS CP2Z19,
    '' AS LIBZ19,
    '' AS CP2Z20,
    '' AS CP2Z21,
    '' AS LIBZ21,
    COALESCE(product_add.default_code, '') AS CP2Z22, -- A vérifier
    COALESCE(bom_line.product_qty, 0) AS CP2Z23, -- A vérifier
    COALESCE(bom_line.product_qty, 0) AS CP2Z24, -- A vérifier
    COALESCE(abc.code, '') AS ABCCOD, -- A vérifier
    product.turnover AS ABCVAV, -- A vérifier
    product.turnover_average AS ABCPCV, -- A vérifier
    product.turnover_nbr_lines AS ABCNLI, -- A vérifier
    product.turnover_average_nbr_lines AS ABCPLI, -- A vérifier
    '' AS ABCPSE,
    product.create_date AS create_date -- Mandatory field used to compute data to export
  FROM product_product AS product
    INNER JOIN product_template AS product_tmpl ON product.product_tmpl_id = product_tmpl.id
    LEFT JOIN product_uom AS purchase_uom ON product_tmpl.uom_po_id = purchase_uom.id
    LEFT JOIN product_uom AS sale_uom ON product_tmpl.uom_id = sale_uom.id
    LEFT JOIN product_template AS product_add_tmpl ON product_add_tmpl.additional_product_id = product_add_tmpl.id
    LEFT JOIN product_product AS product_add ON product_add_tmpl.id = product_add.product_tmpl_id
    LEFT JOIN product_supplierinfo AS supplierinfo ON supplierinfo.id = (SELECT min(id) FROM product_supplierinfo WHERE product_tmpl_id = product_tmpl.id)
    LEFT JOIN res_partner AS supplier ON supplierinfo.name = supplier.id
    LEFT JOIN activity_based_costing AS abc ON product.abc_id = abc.id
    LEFT JOIN product_category AS bu ON product.business_unit_id = bu.id
    LEFT JOIN mrp_bom AS bom ON bom.id = (SELECT min(id) FROM mrp_bom WHERE mrp_bom.product_tmpl_id = product_tmpl.id)
    LEFT JOIN mrp_bom_line AS bom_line ON bom_line.id = (SELECT min(id) FROM mrp_bom_line WHERE mrp_bom_line.bom_id = bom.id AND mrp_bom_line.is_additional_product = TRUE)
    LEFT JOIN product_category AS product_sub_category ON product_tmpl.categ_id = product_sub_category.id
    LEFT JOIN product_category AS product_category ON product_sub_category.parent_id = product_category.id
    LEFT JOIN product_state AS state ON product_tmpl.state_id = state.id
  WHERE product.active = TRUE;
