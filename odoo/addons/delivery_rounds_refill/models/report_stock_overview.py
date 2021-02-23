# -*- coding: utf-8 -*-
# Copyright 2018 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from psycopg2.extensions import AsIs

from odoo import models
from odoo.tools.sql import drop_view_if_exists


class ReportStockOverview(models.Model):
    _name = "report.stock.overview"
    _inherit = "report.stock.overview.abstract"
    _auto = False

    def init(self):
        drop_view_if_exists(self.env.cr, self._table)
        query = """
   WITH warehouse_root_locations As (
    SELECT
        parent_left,
        parent_right,
        sw.id as warehouse_id
    FROM
        stock_location sl
        JOIN stock_warehouse sw on sw.view_location_id = sl.id
   ),
   stock_bykind AS (
    SELECT
      sq.product_id,
      sum(qty) FILTER (WHERE location_kind='bin') as qty_in_bin,
      sum(qty) FILTER (WHERE location_kind='bin' and reservation_id is null) as qty_in_bin_available,
      sum(qty) FILTER (WHERE location_kind='parking') as qty_in_parking,
      sum(qty) FILTER (WHERE location_kind='reserve') as qty_in_reserve,
      warehouse_id
    FROM stock_quant sq
    JOIN stock_location sl on sq.location_id = sl.id
    JOIN warehouse_root_locations wh on wh.parent_left < sl.parent_left and wh.parent_right  > sl.parent_right
    WHERE location_kind IS NOT NULL
    GROUP BY product_id, warehouse_id
  ),
  unreserved_pick_moves AS (
    SELECT
      sm.product_id,
      spt.warehouse_id,
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
      sm.warehouse_id,
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
    GROUP BY sm.product_id, sm.warehouse_id
  )
  SELECT
    concat(warehouse_id, product_id)::integer as id,
    product_id,
    qty_in_bin,
    qty_in_bin_available,
    qty_in_parking,
    qty_in_reserve,
    confirmed_qty,
    confirmed_count,
    planned_qty,
    planned_count,
    immediate_qty,
    immediate_count,
    safety_bin_min_qty,
    warehouse_id,
  CASE
    WHEN coalesce(qty_in_bin_available, 0) < immediate_qty
        THEN 6000 + LEAST(999, confirmed_count)
    WHEN coalesce(qty_in_bin_available, 0) < planned_qty
        THEN 5000 + LEAST(999, confirmed_count)
    WHEN coalesce(qty_in_bin_available, 0) < confirmed_qty
        THEN 1000 + LEAST(999, confirmed_count)
    WHEN coalesce(qty_in_bin, 0) < safety_bin_min_qty
        THEN LEAST(999, average_daily_sales_count)
    ELSE 0
  END AS refill_priority_reassort,
  CASE
    WHEN coalesce(qty_in_bin_available, 0) + coalesce(qty_in_reserve, 0) < immediate_qty
        THEN 6000 + LEAST(999, immediate_count)
    WHEN coalesce(qty_in_bin_available, 0) + coalesce(qty_in_reserve, 0) < planned_qty
        THEN 5000 + LEAST(999, planned_count)
    WHEN coalesce(qty_in_bin_available, 0) + coalesce(qty_in_reserve, 0) < confirmed_qty
        THEN 1000 + LEAST(999, confirmed_count)
    WHEN coalesce(qty_in_bin, 0) + coalesce(qty_in_reserve, 0) < safety_bin_min_qty
        THEN LEAST(999, average_daily_sales_count)
    ELSE 0
  END AS refill_priority_arrange
  FROM stock_bykind
  FULL OUTER JOIN unreserved_pick_moves_byproduct USING (product_id, warehouse_id)
  FULL OUTER JOIN alc_average_daily_sale USING (product_id, warehouse_id)
        """
        self.env.cr.execute(
            "CREATE OR REPLACE VIEW %s AS (%s)", (AsIs(self._table), AsIs(query))
        )
