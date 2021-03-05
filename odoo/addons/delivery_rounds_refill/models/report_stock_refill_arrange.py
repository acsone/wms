# -*- coding: utf-8 -*-
# Copyright 2018 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, models
from odoo.exceptions import UserError


class ReportStockRefillArrange(models.Model):
    _name = "report.stock.refill.arrange"
    _inherit = "report.stock.refill.abstract"
    _auto = False
    _order = "refill_priority_arrange desc"

    def init(self):
        self._create_view("parking")

    def create_picking(self):
        self.ensure_one()

        picking_type = self.location_id.barcode_picking_type_id
        if not picking_type:
            raise UserError(
                _("Missing Operation Type on Location %s")
                % self.location_id.display_name
            )
        picking = self.env["stock.picking"].create(
            {
                "move_type": "direct",
                "company_id": self.location_id.company_id.id,
                "picking_type_id": picking_type.id,
                "origin": "arrange",
                "location_id": self.location_id.id,
                "location_dest_id": picking_type.default_location_dest_id.id,
            }
        )
        picking.button_fillwithstock()

        return picking
