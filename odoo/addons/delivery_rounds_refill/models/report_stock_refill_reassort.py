# -*- coding: utf-8 -*-
# Copyright 2018 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, models
from odoo.exceptions import UserError


class ReportStockRefillReassort(models.Model):
    _name = "report.stock.refill.reassort"
    _inherit = "report.stock.refill.abstract"
    _auto = False
    _order = "refill_priority_reassort desc"

    def init(self):
        self._create_view("reserve")

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
