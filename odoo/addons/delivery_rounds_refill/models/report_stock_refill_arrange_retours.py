# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models
from odoo.tools.sql import drop_view_if_exists

import odoo.addons.decimal_precision as dp
from odoo.addons.stock_storage_type_putaway_abc.models.stock_location import (
    ABC_SELECTION,
)


class ReportStockRefillArrangeRetours(models.Model):
    _name = "report.stock.refill.arrange.retours"
    _auto = False
    _order = "refill_priority_arrange desc"

    product_id = fields.Many2one("product.product", "Product")
    product_uom_id = fields.Many2one(related="product_id.uom_id", readonly=True)
    location_id = fields.Many2one("stock.location", "Location")
    lot_id = fields.Many2one("stock.production.lot", "Lot")
    qty = fields.Float("Quantity")
    reservation_id = fields.Many2one("stock.move", "Reservation")

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
    refill_priority_arrange = fields.Integer("Arrangement Priority")
    safety_bin_min_qty = fields.Float(
        string="Min safety qty into bin",
        digits=dp.get_precision("Product Unit of Measure"),
        help="Minimal safety qty into a bin location",
    )
    abc_classification_level = fields.Selection(
        selection=ABC_SELECTION, required=True, read_only=True, index=True
    )

    @api.model_cr
    def init(self):
        drop_view_if_exists(self._cr, "report_stock_refill_arrange_retours")
        query = """
        CREATE VIEW report_stock_refill_arrange_retours AS (
            WITH return_stock_location AS (
                SELECT
                    parent_left,
                    parent_right
                FROM stock_location sl
                WHERE sl.return_location=true
            )
            SELECT DISTINCT ON (pp.id)
                pp.id as id,
                pp.id as product_id,
                sq.location_id as location_id,
                sq.reservation_id as reservation_id,
                sq.lot_id as lot_id,
                sq.qty as qty,
                rso.refill_priority_arrange as refill_priority_arrange,
                rso.qty_in_bin as qty_in_bin,
                rso.qty_in_bin_available as qty_in_bin_available,
                rso.qty_in_parking as qty_in_parking,
                rso.qty_in_reserve as qty_in_reserve,
                rso.confirmed_qty as confirmed_qty,
                rso.confirmed_count as confirmed_count,
                rso.planned_qty as planned_qty,
                rso.planned_count as planned_count,
                rso.immediate_qty as immediate_qty,
                rso.immediate_count as immediate_count,
                rso.safety_bin_min_qty as safety_bin_min_qty,
                rso.abc_classification_level as abc_classification_level
            FROM stock_quant sq
            JOIN stock_location sl ON sq.location_id = sl.id
            JOIN return_stock_location rsl ON rsl.parent_left < sl.parent_left
                    AND rsl.parent_right > sl.parent_right
            JOIN report_stock_overview rso
                  ON sq.product_id = rso.product_id
            JOIN product_product pp ON pp.id = sq.product_id
            JOIN product_template pt ON pt.id = pp.product_tmpl_id
            LEFT JOIN stock_production_lot spl ON sq.lot_id = spl.id
            WHERE sl.usage = 'internal'
        )
        """
        self._cr.execute(query)
