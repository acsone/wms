CREATE OR REPLACE VIEW zelapro_export_suppliers AS
  SELECT
    supplier.ref AS FOUNUM,
    '' AS FOULAN,
    supplier.name AS FOUNOM,
    '' AS FOUNOS,
    '' AS FOUADR,
    '' AS FOUCPO,
    '' AS FOULOC,
    '' AS FOUAPP,
    '' AS FOUCEE,
    '' AS FOUDIV,
    '' AS LIBDIV,
    '' AS FOUTIT,
    '' AS FOUDEV,
    '' AS LIBDEV,
    '' AS FOUPRF,
    categ.name AS LIBPRF,
    '' AS FOUTEL,
    '' AS FOUFAX,
    '' AS PAACPT,
    '' AS PAANBQ,
    '' AS PAASWI,
    COALESCE(supplier.delivery_lead_time, 0) AS FOUDLL, -- TODO A charger !!!
    '' AS FOURES,
    '' AS LIBRES,
    '' AS FOUJES,
    '' AS LIBJES,
    '' AS FOUPOU,
    '' AS LIBPOU,
    '' AS FOUGES,
    '' AS LIBGES,
    COALESCE(supplier.supplier_discount, 0) AS FOUREM, -- TODO A charger !!!
    supplier.create_date AS create_date -- Mandatory field used to compute data to export
  FROM res_partner AS supplier
    LEFT JOIN partner_alcyon_category AS categ ON supplier.alcyon_category_id = categ.id
  WHERE supplier.supplier = TRUE
    AND supplier.active = TRUE;
