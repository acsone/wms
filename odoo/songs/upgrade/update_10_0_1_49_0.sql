UPDATE ir_model_data
SET module = 'specific_data'
WHERE module = 'stock_delivery_note'
AND name = 'vat_tax_group';
