# -*- coding: utf-8 -*-
# Copyright 2018 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, fields, models
from odoo.exceptions import UserError
from odoo.tools.sql import drop_view_if_exists


class ReportStockRefillReassort(models.Model):
    _name = "report.stock.refill.reassort"
    _auto = False
    _order = "refill_priority_reassort desc"

    def init(self):
        drop_view_if_exists(self.env.cr, self._table)
        query = """
          SELECT distinct ON (product_id)
            sq.location_id,
            sq.reservation_id,
            sq.lot_id, sq.qty, rso.*
          FROM stock_quant sq
          JOIN stock_location sl ON sq.location_id = sl.id
          JOIN report_stock_overview rso USING (product_id)
          LEFT JOIN stock_production_lot lot ON sq.lot_id = lot.id
          WHERE sl.kind = 'reserve'
            AND rso.qty_in_reserve > 0
          ORDER BY product_id, lot.removal_date, sq.in_date
        """
        self.env.cr.execute(
            "CREATE OR REPLACE VIEW " + self._table + " AS (" + query + ")"
        )

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

    average_qty = fields.Integer(
        "Average daily usage",
        help="Computed with an horizon of 1 week assuming 5 working days",
    )
    average_count = fields.Integer(
        "Average daily customer",
        help="Computed with an horizon of 1 week assuming 5 working days",
    )

    refill_priority_reassort = fields.Integer("Reassortment Priority")

    def create_picking(self):
        self.ensure_one()

        picking_type = self.location_id.barcode_picking_type_id
        if not picking_type:
            raise UserError(
                _("Missing operation type on location %s")
                % self.location_id.display_name
            )
        picking = self.env["stock.picking"].create(
            {
                "move_type": "direct",
                "company_id": self.location_id.company_id.id,
                "picking_type_id": picking_type.id,
                "origin": "reassort",
                "location_id": self.location_id.id,
                "location_dest_id": picking_type.default_location_dest_id.id,
                "move_lines": [
                    (
                        0,
                        False,
                        {
                            "name": self.product_id.display_name,
                            "product_id": self.product_id.id,
                            "product_uom": self.product_id.uom_id.id,
                            "product_uom_qty": self.qty,
                            "location_id": self.location_id.id,
                            "location_dest_id": picking_type.default_location_dest_id.id,
                        },
                    )
                ],
            }
        )
        picking.action_assign()
        return picking
