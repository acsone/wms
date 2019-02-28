INSERT INTO ir_model_data
(create_uid, create_date, write_uid, write_date,
 date_init, date_update, noupdate,
 module, name, model, res_id)
SELECT 1, now(), 1, now(),
 now(), now(), true,
 'specific_base', 'stock_location_vlb', 'stock.location', l.id
FROM stock_location l
WHERE l.name = 'VLB'
AND NOT EXISTS (
  SELECT id FROM ir_model_data WHERE
  module = 'specific_base'
  AND name = 'stock_location_vlb'
);
