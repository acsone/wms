# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from psycopg2.extensions import AsIs

from odoo import fields, models
from odoo.tools.sql import drop_view_if_exists


class ReportStockRefillAbstract(models.AbstractModel):
    _name = "report.stock.refill.abstract"
    _inherit = "report.stock.overview.abstract"
    _auto = False
    _order = "refill_priority_arrange desc"

    product_uom_id = fields.Many2one(related="product_id.uom_id", readonly=True)
    location_id = fields.Many2one("stock.location", "Location")
    lot_id = fields.Many2one("stock.production.lot", "Lot")
    qty = fields.Float("Quantity")
    reservation_id = fields.Many2one("stock.move", "Reservation")

    def _create_view(self, location_kind):
        qty_field = "qty_in_reserve"
        if location_kind == "parking":
            qty_field = "qty_in_parking"
        drop_view_if_exists(self.env.cr, self._table)
        query = """
        CREATE OR REPLACE VIEW %s AS (
            WITH warehouse_root_locations As (
                SELECT
                    parent_left,
                    parent_right,
                    sw.id as warehouse_id
                FROM
                    stock_location sl
                    JOIN stock_warehouse sw on sw.view_location_id = sl.id
            )
              SELECT DISTINCT ON (rso.id)
                sq.location_id,
                sq.reservation_id,
                sq.lot_id, sq.qty, rso.*
              FROM stock_quant sq
              JOIN stock_location sl on sq.location_id = sl.id
              JOIN warehouse_root_locations wh
                  ON wh.parent_left < sl.parent_left
                     AND wh.parent_right > sl.parent_right
              JOIN report_stock_overview rso
                  ON sq.product_id = rso.product_id
                     AND rso.warehouse_id = wh.warehouse_id
              LEFT JOIN stock_production_lot lot ON sq.lot_id = lot.id
              WHERE sq.location_kind = %s
                AND rso.%s > 0
              ORDER BY rso.id, product_id, lot.removal_date, sq.in_date
        )
        """
        self.env.cr.execute(query, (AsIs(self._table), location_kind, AsIs(qty_field)))
