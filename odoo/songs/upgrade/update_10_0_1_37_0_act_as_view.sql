-- besides the 'view location' of the warehouse,
-- all the locations with usage 'view' must be 'internal'
-- as we have bugs with 'view'
UPDATE
  stock_location
SET
  usage = 'internal'
, act_as_view = true
WHERE
  usage = 'view'
  AND id NOT IN (SELECT view_location_id FROM stock_warehouse)
  -- the top-level locations (Partner, Physical, Virtual) must
  -- remain views
  AND location_id IS NOT NULL;


-- the Stock location has already been updated manually
-- in production to 'internal' so won't be catch by the
-- first UPDATE
UPDATE
stock_location
SET
usage = 'internal'
, act_as_view = true
WHERE
  id IN (SELECT res_id
         FROM ir_model_data
         WHERE module = 'stock'
         AND name = 'stock_location_stock');
