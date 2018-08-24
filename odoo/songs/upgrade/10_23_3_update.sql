-- Fix field partner_invoice_id on already imported sale orders to reflect
-- the new hierarchy.
--
-- Invoice partner is the main company on not the contact in many cases.

WITH t AS (
   SELECT so.id, parent.id as new_invoice_partner
   FROM sale_order so
   INNER JOIN res_partner p ON so.partner_id = p.id
   INNER JOIN res_partner parent ON parent.id = p.parent_id
   WHERE parent.type = 'invoice'
     AND so.partner_invoice_id <> parent.id
)
UPDATE
   sale_order AS so
 SET
   partner_invoice_id = t.new_invoice_partner
 FROM t
 WHERE so.id = t.id;
