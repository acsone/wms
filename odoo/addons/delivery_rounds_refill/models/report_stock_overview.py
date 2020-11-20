# -*- coding: utf-8 -*-
# Copyright 2018 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models
from odoo.tools.sql import drop_view_if_exists


class ReportStockOverview(models.Model):
    _name = "report.stock.overview"
    _auto = False

    def init(self):
        drop_view_if_exists(self.env.cr, self._table)
        query = """
  WITH stock_bykind AS (
    SELECT
      sq.product_id,
      sum(qty) FILTER (WHERE location_kind='bin') as qty_in_bin,
      sum(qty) FILTER (WHERE location_kind='bin' and reservation_id is null) as qty_in_bin_available,
      sum(qty) FILTER (WHERE location_kind='parking') as qty_in_parking,
      sum(qty) FILTER (WHERE location_kind='reserve') as qty_in_reserve
    FROM stock_quant sq
    WHERE location_kind IS NOT NULL
    GROUP BY product_id
  ),
  unreserved_pick_moves AS (
    SELECT
      sm.product_id,
      CASE
        WHEN state = 'confirmed' THEN sm.product_uom_qty
        ELSE sm.product_uom_qty - (SELECT sum(qty) FROM stock_quant WHERE reservation_id=sm.id)
      END AS missing_qty,
      sm.picking_id
    FROM stock_move sm
    JOIN stock_picking_type spt ON sm.picking_type_id=spt.id
    WHERE
      spt.subcode = 'PICK'
      AND sm.priority > '0' -- to exclude palette
      AND sm.procure_method = 'make_to_stock'
      AND (sm.state = 'confirmed' or (sm.state = 'assigned' and sm.partially_available))
  ),
  unreserved_pick_moves_byproduct AS (
    SELECT
      sm.product_id,
      sum(missing_qty) AS confirmed_qty,
      count(distinct partner_id) AS confirmed_count,
      SUM(missing_qty)
        FILTER (WHERE ri.id IS NOT NULL) AS planned_qty,
      count(distinct partner_id)
        FILTER (WHERE ri.id IS NOT NULL) AS planned_count,
      SUM(missing_qty)
        FILTER (WHERE ri.picking_launched) AS immediate_qty,
      count(distinct partner_id)
        FILTER (WHERE ri.picking_launched) AS immediate_count
    FROM unreserved_pick_moves sm
    LEFT JOIN stock_picking sp ON sm.picking_id = sp.id
    LEFT JOIN round_instance ri ON sp.delivery_round_id = ri.id
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
      -- consider an horizon of 1 week, exclude today
      AND sm.date BETWEEN (NOW() - INTERVAL '7 DAY')::date
                      AND (NOW())::date
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
    WHEN coalesce(qty_in_bin_available, 0) < immediate_qty
        THEN 6000 + LEAST(999, confirmed_count)
    WHEN coalesce(qty_in_bin_available, 0) < planned_qty
        THEN 5000 + LEAST(999, confirmed_count)
    WHEN coalesce(qty_in_bin_available, 0) < confirmed_qty
        THEN 1000 + LEAST(999, confirmed_count)
    -- Days to cover = 2
    WHEN coalesce(qty_in_bin, 0) < average_qty*2
        THEN LEAST(999, average_count)
    ELSE 0
  END AS refill_priority_reassort,
  CASE
    WHEN coalesce(qty_in_bin_available, 0) + coalesce(qty_in_reserve, 0) < immediate_qty
        THEN 6000 + LEAST(999, immediate_count)
    WHEN coalesce(qty_in_bin_available, 0) + coalesce(qty_in_reserve, 0) < planned_qty
        THEN 5000 + LEAST(999, planned_count)
    WHEN coalesce(qty_in_bin_available, 0) + coalesce(qty_in_reserve, 0) < confirmed_qty
        THEN 1000 + LEAST(999, confirmed_count)
    -- Days to cover = 2
    WHEN coalesce(qty_in_bin, 0) + coalesce(qty_in_reserve, 0) < average_qty*2
        THEN LEAST(999, average_count)
    ELSE 0
  END AS refill_priority_arrange
  FROM stock_bykind
  FULL OUTER JOIN unreserved_pick_moves_byproduct USING (product_id)
  FULL OUTER JOIN deliveries_last_byproduct USING (product_id)
        """
        self.env.cr.execute(
            "CREATE OR REPLACE VIEW " + self._table + " AS (" + query + ")"
        )

    product_id = fields.Many2one("product.product", "Product")

    qty_in_bin = fields.Float("Quantity in bin")
    qty_in_bin_available = fields.Float("Quantity available in bin")
    qty_in_parking = fields.Float("Quantity in parking")
    qty_in_reserve = fields.Float("Quantity in reserve")

    confirmed_qty = fields.Integer(
        "Quantity to pick", help="Remaining quantity to pick"
    )
    confirmed_count = fields.Integer(
        "Customers to pick",
        help="Amount of customers having a remaining quantity to pick",
    )
    planned_qty = fields.Integer(
        "Planned quantity to pick",
        help="Remaining quantity to pick in a planned delivery round",
    )
    planned_count = fields.Integer(
        "Planned customers to pick",
        help="Amount of customers having a remaining quantity to pick"
        " in a planned delivery round",
    )
    immediate_qty = fields.Integer(
        "Immediate quantity to pick",
        help="Remaining quantity to pick in a stared delivery round",
    )
    immediate_count = fields.Integer(
        "Immediate customers to pick",
        help="Amount of customers having a remaining quantity to pick"
        " in a started delivery round",
    )

    average_qty = fields.Integer(
        "Average daily usage",
        help="Computed with an horizon of 1 week assuming 5 working days",
    )
    average_count = fields.Integer(
        "Average daily customer",
        help="Computed with an horizon of 1 week assuming 5 working days",
    )

    refill_priority_arrange = fields.Integer("Arrangement Priority")
    refill_priority_reassort = fields.Integer("Reassortment Priority")
