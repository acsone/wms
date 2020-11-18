# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockQuant(models.Model):

    _inherit = "stock.quant"

    location_kind = fields.Selection(
        selection="_selection_location_lind",
        related="location_id.kind",
        store=True,
        index=True,
    )

    @api.model
    def _selection_location_lind(self):
        return self.env["location_id"]._fields["kind"].selecction
