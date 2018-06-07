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

DELETE FROM sale_order WHERE

-- remove sale orders of type 2
-- do this only if db2_pentcdcl is present as we need to read from it
-- we let the sale order in 'sale' state as they created pickings and
-- pack operations. This would require more in depth changes that might
-- not be worth it for testing purpose.
DO $$
BEGIN
    IF EXISTS
        ( SELECT 1
            FROM  information_schema.tables
            WHERE table_schema = 'public'
            AND   table_name = 'db2_pentcdcl'
        )
    THEN
        RAISE NOTICE 'Calling delete sale order type 2, this can take several minutes';
        DELETE FROM sale_order
            USING db2_pentcdcl
            WHERE sale_order.name = eccsui::varchar
              AND ecctyc = '2'
              AND state in ('draft', 'done');
    END IF;
END$$;
