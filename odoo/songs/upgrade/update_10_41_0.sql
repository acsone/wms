-- remove incorrect and not more used xmlid
DELETE FROM ir_model_data
WHERE model='specific_data' and name='deliver_carrier_alcyon_product_product';
