-- The column stock_pack_operation.additional_move is no longer
-- used, and empty in production (replaced by additional_move_id).
-- It can't be removed because the view 'stock_pack_operation_operator'
-- uses all the fields of stock_pack_operation.
-- This field has a FK on stock_move, and slows down a DELETE on stock_move
-- which has to do a seqscan on the stock_pack_operation to see if there is
-- no additional_move, but the field is guaranteed to be empty... remove it
-- and the related data (we have to drop and recreate the view to do so).
DROP VIEW stock_pack_operation_operator;
ALTER TABLE stock_pack_operation
DROP CONSTRAINT IF EXISTS stock_pack_operation_additional_move_fkey;

DELETE FROM ir_model_data
WHERE
  module = 'product_additional'
  AND name = 'field_stock_pack_operation_additional_move';

DELETE FROM ir_model_fields
WHERE
  name = 'additional_move'
  AND model_id = (
    SELECT id FROM ir_model
    WHERE model = 'stock.pack.operation'
  );
ALTER TABLE stock_pack_operation
DROP COLUMN IF EXISTS additional_move;
CREATE VIEW stock_pack_operation_operator AS (
  SELECT
    spo.*,
    sp.operator_id as operator_id
    FROM
        stock_pack_operation as spo
        JOIN
        stock_picking as sp
            ON sp.id = spo.picking_id
);

-- Create indexes, they are added in the local modules,
-- but we spare an upgrade of these modules by creating them manually.
-- All these indexes reference 'stock_move' and not having them slows
-- down DELETE operations on stock.move (~6s for a DELETE).
CREATE INDEX IF NOT EXISTS
stock_pack_operation_additional_move_id_index
ON stock_pack_operation(additional_move_id);
CREATE INDEX IF NOT EXISTS
  stock_move_split_from_index ON stock_move(split_from);
CREATE INDEX IF NOT EXISTS
  stock_quant_negative_move_id_index ON stock_quant(negative_move_id);
CREATE INDEX IF NOT EXISTS
  stock_move_origin_returned_move_id_index ON stock_move(origin_returned_move_id);
CREATE INDEX IF NOT EXISTS
  procurement_order_move_dest_id_index ON procurement_order(move_dest_id);
CREATE INDEX IF NOT EXISTS
  stock_move_inventory_id_index ON stock_move(inventory_id);

/*
This is what is asked for :
Check all the products with an empty vendor_product_code
For the empty ones, check the value of the supplier info records, if one 
is filled for the product code but others are not then fill the empty ones with the value
of the filled one.
Check ALCYN-2322

A dash in the product_code is treated like an empty value.
There is NO product_supplierinfo with a product_code set to an empty string

After this script there is 21 product with product_supplierinfo.product_code with 2 or
more distinct values that need to be handled by hand.
*/


UPDATE product_supplierinfo
    SET product_code = (
        SELECT DISTINCT(product_code) 
            FROM product_supplierinfo AS goodsupplierinfo 
            WHERE goodsupplierinfo.product_tmpl_id = tempdb.id
                  AND COALESCE(product_code, '-') <> '-')
    FROM (
            SELECT pt.id
                FROM product_template AS pt
                INNER JOIN product_supplierinfo AS psi ON pt.id = psi.product_tmpl_id
                WHERE (pt.vendor_product_code = '' OR pt.vendor_product_code IS NULL)
                GROUP BY pt.id, pt.name HAVING count(DISTINCT(coalesce(psi.product_code,'-'))) = 2
        ) tempdb
    WHERE product_supplierinfo.product_tmpl_id = tempdb.id
          AND COALESCE(product_supplierinfo.product_code, '-') = '-'
;
