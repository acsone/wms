CREATE OR REPLACE VIEW zelapro_export_contacts AS
  SELECT
    partner.ref AS CCFNUM,
    '' AS CCFCON,
    partner.name AS CCFNOM,
    CASE
      WHEN lang.code LIKE 'fr%' THEN 'FR'
      WHEN lang.code = 'nl%' THEN 'NL'
      WHEN lang.code = 'nl_BE' THEN 'D'
      ELSE ''
    END AS CCFLAN,
    '' AS CCFSRV,
    partner.function AS CCFFON,
    CASE
      WHEN NULLIF(partner.phone, '') IS NULL THEN partner.phone
      ELSE partner.mobile
    END AS CCFTLP,
    '' AS CCFTEL,
    partner.phone AS CCFFAX,
    partner.comment AS CCFTEX,
    partner.email AS EMWADR
  FROM res_partner AS partner
    LEFT JOIN res_lang AS lang ON partner.lang = lang.id
  WHERE partner.supplier = TRUE;