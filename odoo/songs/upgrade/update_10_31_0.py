# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


import anthem


@anthem.log
def correct_stock_operation_locations(ctx):
    """Correct locations of stock moves

    We have ~4000 stock moves Suppliers -> Reception which are related to
    quants in a location named "[MIGRATION] Réception achats". The problem is,
    this location has been moved and is no longer a sublocation of Reception,
    which means the total quantities of stock moves and stock quants do not
    agree when it comes to know the quantity in internal locations / below VLB.

    At some points, moves were generated with a source/dest
    location which was under VLB, then location was moved out of VLB.
    Result is that we have quants not considered in Stock history for moves
    considered in stock history.

    Remap the correct locations on these moves based on the locations
    of the stock operations, which have the correct sublocations.

    """
    ctx.env.cr.execute("""
UPDATE stock_move
SET location_dest_id = buggy_moves.operation_location_dest_id
FROM (
    WITH vlb AS (
    SELECT parent_left, parent_right
    FROM stock_location
    WHERE id = (SELECT res_id
                FROM ir_model_data
                WHERE module = 'specific_base'
                AND name = 'stock_location_vlb')
  ), vlb_sublocations AS (
    SELECT id FROM stock_location
    WHERE parent_left >= (select parent_left from vlb)
    AND parent_right <= (select parent_right from vlb)
  )
  SELECT move.id,
         operation.location_dest_id as operation_location_dest_id
  FROM stock_move move
  JOIN stock_move_operation_link link
  ON link.move_id = move.id
  JOIN stock_pack_operation operation
  ON operation.id = link.operation_id
  WHERE
    move.location_dest_id != operation.location_dest_id
    AND
    (
    move.location_dest_id IN (SELECT id FROM vlb_sublocations)
    AND operation.location_dest_id NOT IN (SELECT id FROM vlb_sublocations)
    OR
    move.location_dest_id NOT IN (SELECT id FROM vlb_sublocations)
    AND operation.location_dest_id IN (SELECT id FROM vlb_sublocations)
    )) AS buggy_moves
WHERE stock_move.id = buggy_moves.id
;
    """)

    ctx.env.cr.execute("""
UPDATE stock_move
SET location_id = buggy_moves.operation_location_id
FROM (
    WITH vlb AS (
    SELECT parent_left, parent_right
    FROM stock_location
    WHERE id = (SELECT res_id
                FROM ir_model_data
                WHERE module = 'specific_base'
                AND name = 'stock_location_vlb')
  ), vlb_sublocations AS (
    SELECT id FROM stock_location
    WHERE parent_left >= (select parent_left from vlb)
    AND parent_right <= (select parent_right from vlb)
  )
  SELECT move.id,
         operation.location_id as operation_location_id
  FROM stock_move move
  JOIN stock_move_operation_link link
  ON link.move_id = move.id
  JOIN stock_pack_operation operation
  ON operation.id = link.operation_id
  WHERE
    move.location_id != operation.location_id
    AND
    (
    move.location_id IN (SELECT id FROM vlb_sublocations)
    AND operation.location_id NOT IN (SELECT id FROM vlb_sublocations)
    OR
    move.location_id NOT IN (SELECT id FROM vlb_sublocations)
    AND operation.location_id IN (SELECT id FROM vlb_sublocations)
    )) AS buggy_moves
WHERE stock_move.id = buggy_moves.id
;
    """)


@anthem.log
def reload_translation(ctx):
    """ update translation """
    ctx.env['ir.module.module'].with_context(overwrite=True).search(
        [('name', '=', 'specific_report')]
    ).update_translations()


@anthem.log
def post(ctx):
    reload_translation(ctx)
