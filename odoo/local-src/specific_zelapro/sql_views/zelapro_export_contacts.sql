CREATE OR REPLACE VIEW zelapro_export_contacts AS
  SELECT
    partner.ref AS CCFNUM,
    '' AS CCFCON,
    '' AS CCFNOM,
    CASE
      WHEN partner.lang LIKE 'fr%' THEN 'FR'
      WHEN partner.lang LIKE 'nl%' THEN 'NL'
      WHEN partner.lang LIKE 'de%' THEN 'D'
      ELSE ''
    END AS CCFLAN,
    '' AS CCFSRV,
    '' AS CCFFON,
    '' AS CCFTLP,
    '' AS CCFTEL,
    '' AS CCFFAX,
    '' AS CCFTEX,
    '' AS EMWADR,
    partner.create_date AS create_date
  FROM res_partner AS partner
  WHERE partner.supplier = TRUE;