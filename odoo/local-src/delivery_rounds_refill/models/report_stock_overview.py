# -*- coding: utf-8 -*-
# Copyright 2018 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models
from odoo.tools.sql import drop_view_if_exists


class ReportStockOverview(models.Model):
    _name = 'report.stock.overview'
    _auto = False

    def init(self):
        drop_view_if_exists(self.env.cr, self._table)
        query = """
  WITH stock_bykind AS (
    SELECT
      sq.product_id,
      sum(qty) FILTER (WHERE sl.kind='bin') as qty_in_bin,
      sum(qty) FILTER (WHERE sl.kind='parking') as qty_in_parking,
      sum(qty) FILTER (WHERE sl.kind='reserve') as qty_in_reserve
    FROM stock_quant sq
    JOIN stock_location sl ON sq.location_id = sl.id
    WHERE sl.kind IS NOT NULL
    GROUP BY product_id
  ),
  deliveries_todo AS (
    SELECT
      sm.id,
      sm.product_id,
      sm.product_uom_qty,
      sm.picking_id
    FROM stock_move sm
    JOIN stock_location sl_src ON sm.location_id = sl_src.id
    JOIN stock_location sl_dest ON sm.location_dest_id = sl_dest.id
    WHERE
      sl_src.usage in ('view', 'internal')
      AND sl_dest.usage = 'customer'
      AND sm.priority > '0'
      AND sm.state not in ('cancel', 'done', 'draft')
  ),
  pending_deliveries_reserved_by_product AS (
    -- quantities reserved for pending delivery round instances
    SELECT
      sm.product_id,
      sum(quant.qty) as reserved_qty_pending
    FROM stock_move sm
    JOIN stock_picking  sp  ON (sm.picking_id = sp.id)
    JOIN stock_picking_type spt ON (sp.picking_type_id = spt.id and spt.code='internal')
    JOIN round_instance ri ON (sp.delivery_round_id = ri.id)
    JOIN stock_quant quant ON (quant.reservation_id = sm.id)
    WHERE NOT ri.picking_launched
    GROUP BY sm.product_id
  ),
  deliveries_todo_byproduct AS (
    SELECT
      sm.product_id,
      sum(product_uom_qty) AS confirmed_qty,
      count(product_uom_qty) AS confirmed_count,
      sum(COALESCE(p_deli.reserved_qty_pending, 0.)) AS pending_round_reserved_qty,
      sum(product_uom_qty)
        FILTER (WHERE ri.id IS NOT NULL) AS planned_qty,
      count(product_uom_qty)
        FILTER (WHERE ri.id IS NOT NULL) AS planned_count,
      sum(product_uom_qty)
        FILTER (WHERE ri.picking_launched) AS immediate_qty,
      count(product_uom_qty)
        FILTER (WHERE ri.picking_launched) AS immediate_count
    FROM deliveries_todo sm
    LEFT JOIN stock_picking sp ON sm.picking_id = sp.id
    LEFT JOIN round_instance ri ON sp.delivery_round_id = ri.id
    LEFT JOIN pending_deliveries_reserved_by_product p_deli ON (p_deli.product_id = sm.product_id)
    GROUP BY sm.product_id
  ),
  deliveries_last AS (
    SELECT
      sm.product_id,
      sm.product_uom_qty,
      (avg(product_uom_qty) OVER pid
       - stddev_samp(product_uom_qty) OVER pid * 2) as lower_bound,
      (avg(product_uom_qty) OVER pid
       + stddev_samp(product_uom_qty) OVER pid * 2) as upper_bound
    FROM stock_move sm
    JOIN stock_location sl_src ON sm.location_id = sl_src.id
    JOIN stock_location sl_dest ON sm.location_dest_id = sl_dest.id
    WHERE
      sl_src.usage in ('view', 'internal')
      AND sl_dest.usage = 'customer'
      AND sm.priority > '0'
      AND sm.date BETWEEN (NOW() - INTERVAL '7 DAY')::date
                      AND (NOW() - INTERVAL '1 DAY')::date
      AND sm.state = 'done'
    WINDOW pid AS (PARTITION BY sm.product_id)
  ),
  deliveries_last_byproduct AS (
    SELECT
      product_id,
      ceil(avg(product_uom_qty) FILTER
        (WHERE product_uom_qty BETWEEN lower_bound AND upper_bound)
        -- consider 5 open days on 7
        / 5.0) AS average_qty,
      ceil(count(product_uom_qty) FILTER
        (WHERE product_uom_qty BETWEEN lower_bound AND upper_bound)
        / 5.0) AS average_count
    FROM deliveries_last
    GROUP BY product_id
  )
  SELECT product_id AS id, *,
  CASE
    WHEN coalesce(qty_in_bin, 0) - coalesce(pending_round_reserved_qty, 0) < immediate_qty
        THEN 6000 + LEAST(999, immediate_count)
    WHEN coalesce(qty_in_bin, 0) < planned_qty
        THEN 5000 + LEAST(999, planned_count)
    WHEN coalesce(qty_in_bin, 0) < confirmed_qty
        THEN 1000 + LEAST(999, confirmed_count)
    -- Days to cover = 2
    WHEN coalesce(qty_in_bin, 0) < average_qty*2
        THEN LEAST(999, average_count)
    ELSE 0
  END AS refill_priority_reassort,
  CASE
    WHEN coalesce(qty_in_bin, 0) + coalesce(qty_in_reserve, 0) - coalesce(pending_round_reserved_qty, 0) < immediate_qty
        THEN 6000 + LEAST(999, immediate_count)
    WHEN coalesce(qty_in_bin, 0) + coalesce(qty_in_reserve, 0) < planned_qty
        THEN 5000 + LEAST(999, planned_count)
    WHEN coalesce(qty_in_bin, 0) + coalesce(qty_in_reserve, 0) < confirmed_qty
        THEN 1000 + LEAST(999, confirmed_count)
    -- Days to cover = 2
    WHEN coalesce(qty_in_bin, 0) + coalesce(qty_in_reserve, 0) < average_qty*2
        THEN LEAST(999, average_count)
    ELSE 0
  END AS refill_priority_arrange
  FROM stock_bykind
  FULL OUTER JOIN deliveries_todo_byproduct USING (product_id)
  FULL OUTER JOIN deliveries_last_byproduct USING (product_id)
        """
        self.env.cr.execute(
            "CREATE OR REPLACE VIEW " + self._table + " AS (" + query + ")"
        )

    product_id = fields.Many2one('product.product', 'Product')

    qty_in_bin = fields.Float('Quantity in bin')
    qty_in_parking = fields.Float('Quantity in parking')
    qty_in_reserve = fields.Float('Quantity in reserve')

    confirmed_qty = fields.Integer('Confirmed outgoing qty')
    confirmed_count = fields.Integer('Confirmed outgoing count')
    planned_qty = fields.Integer('Planned outgoing qty')
    planned_count = fields.Integer('Planned outgoing count')
    immediate_qty = fields.Integer('Immediate outgoing qty')
    pending_round_reserved_qty = fields.Integer(
        'Reserved qty in bin',
        help="Quantity in bin, reserved for delivery rounds which "
        "are not started",
    )
    immediate_count = fields.Integer('Immediate outgoing count')
    average_qty = fields.Integer('Average outgoing qty')
    average_count = fields.Integer('Average outgoing count')

    refill_priority_arrange = fields.Integer('Arrangement Priority')
    refill_priority_reassort = fields.Integer('Reassortment Priority')
