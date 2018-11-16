-- trash all bins previously imported to recreate them
TRUNCATE product_stock_bin;
DELETE FROM ir_model_data WHERE model = 'product.stock.bin' and module = '__import__';

-- remove all new routes from products to recreate them
DELETE FROM stock_route_product WHERE route_id = (SELECT id FROM stock_location_route WHERE name = 'Nouveauté');

-- description_picking must be emptied to be filled again later
UPDATE product_template SET description_picking = '' WHERE description_picking != '';

-- trash all supplierinfo previously imported to recreate them
TRUNCATE product_supplierinfo;
DELETE FROM ir_model_data WHERE model = 'product.supplierinfo' and module = '__import__';
