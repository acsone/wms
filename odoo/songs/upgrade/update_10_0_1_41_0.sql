-- This script adds ignore_exception column on sale_order_line and update its
-- values.
-- As sale_order_line.ignore_exception is a related field on
-- sale_order.ignore_exception, we use SQL to avoid having Odoo computing the
-- the value for each existing line, as we can set it in a single UPDATE.
-- On DEV instance with PROD DB copy, this update of 3007364 lines
-- took 3 mins and 18 seconds to complete
ALTER TABLE sale_order_line
ADD COLUMN ignore_exception bool NULL;

UPDATE sale_order_line sol
SET sol.ignore_exception = so.ignore_exception
FROM sale_order so
WHERE sol.order_id = so.id;
