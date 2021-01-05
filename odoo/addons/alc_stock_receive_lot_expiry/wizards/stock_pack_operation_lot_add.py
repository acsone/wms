# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockPackOperationLotAdd(models.TransientModel):

    _inherit = "stock.pack.operation.lot.add"

    is_removal_date_expired = fields.Boolean(
        "Removal Date Expired", compute="_compute_is_removal_date_expired"
    )

    @api.depends("life_date", "operation_id")
    def _compute_is_removal_date_expired(self):
        if not self.operation_id:
            self.is_removal_date_expired = False
        else:
            lot = self.env["stock.production.lot"].new(
                {
                    "product_id": self.operation_id.product_id.id,
                    "life_date": self.life_date,
                }
            )
            self._lot_onchange_life_date(lot)
            self.is_removal_date_expired = lot.is_expired
