# -*- coding: utf-8 -*-
# © 2018 Sylvain Van Hoof (Okia SPRL)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models

from .. import constants


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    zetes_picking_type = fields.Selection(
        [
            (constants.PICKING_ASSIGNMENT, "Customer"),
            (constants.RANGEMENT_ASSIGNMENT, "Rangement"),
            (constants.REASSORT_ASSIGNMENT, "Reassort"),
        ],
        string="Picking type",
    )

    passport = fields.Boolean("Enable passports")

    def toggle_passport(self):
        for rec in self:
            rec.passport = not rec.passport
