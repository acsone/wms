-- This script updates XML IDs of records whose data files were moved from
-- anthem scripts to specific_data module.
UPDATE ir_model_data
SET module = 'specific_data'
WHERE module = '__setup__'
AND model = 'product.category';

UPDATE ir_model_data
SET module = 'specific_data'
WHERE module = '__setup__'
AND model = 'res.partner.category';

UPDATE ir_model_data
SET module = 'specific_data'
WHERE module = '__setup__'
AND model = 'product.pricelist'
AND name = 'product_pricelist_pb2';
