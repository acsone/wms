-- increase sequence to lower the priority of all supplierinfo without end date, bounded supplierinfo must come first
UPDATE product_supplierinfo SET sequence = 100 WHERE date_end IS NULL;

-- discount field on sale order line should not be used
-- partially repair discount, we are missing the data for discount2
-- the query to update discount2 could take a long time
-- To do manually
-- UPDATE sale_order_line SET discount2 = dccres FROM db2_pdetcdcl inner join sale_order as so on
--   dccsui = so.name::int WHERE sale_order_line.order_id = so.id and sale_order_line.sequence = dccnli and dccres > 0 and dccres <= 100;
UPDATE sale_order_line SET discount3 = discount WHERE discount > 0 and discount <= 100;
UPDATE sale_order_line SET discount = 0 WHERE discount > 0;
