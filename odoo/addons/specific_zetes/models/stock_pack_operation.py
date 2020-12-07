# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockPackOperation(models.Model):

    _inherit = "stock.pack.operation"

    @api.multi
    def unlink(self):
        # track deleted pack operation...
        for record in self:
            self.env["stock.pack.operation.deleted"].create(
                {
                    "deleted_id": record.id,
                    "picking_id": record.picking_id.id,
                    "product_id": record.product_id.id,
                }
            )
        return super(StockPackOperation, self).unlink()
