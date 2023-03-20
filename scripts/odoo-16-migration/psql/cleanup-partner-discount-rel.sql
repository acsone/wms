\set ON_ERROR_STOP

DELETE FROM partner_discount_pricelist_rel WHERE NOT EXISTS (SELECT id FROM res_partner AS rp WHERE rp.id = partner_id );
