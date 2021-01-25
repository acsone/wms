# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockQuant(models.Model):

    _inherit = "stock.quant"

    location_kind = fields.Selection(
        selection="_selection_location_kind",
        related="location_id.kind",
        store=True,
        index=True,
        readonly=True,
    )

    @api.model_cr
    def init(self):
        res = super(StockQuant, self).init()
        # This partial index is used by the 'has_pending_reassort' computed field
        # on 'round.instance'
        query = """
            CREATE INDEX IF NOT EXISTS
            stock_quant_positive_qty_location_type_index
            ON stock_quant (product_id, location_kind)
            WHERE qty > 0;
        """
        self.env.cr.execute(query)
        return res

    @api.model
    def _selection_location_kind(self):
        return self.env["location_id"]._fields["kind"].selection
