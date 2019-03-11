UPDATE ir_model_data
SET module = 'specific_data'
WHERE module = '__setup__'
AND name = 'deliver_carrier_alcyon_product_product';
