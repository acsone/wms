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
