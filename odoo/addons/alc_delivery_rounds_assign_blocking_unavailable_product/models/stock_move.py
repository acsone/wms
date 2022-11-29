# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockMove(models.Model):

    _inherit = "stock.move"

    # a pocking can be assigned to a delivery round only if
    # we've at lease one stock.move with delivery_requires_other_lines not set
    # for the same partner for all the pickings candidate to the delivery
    product_qty_unavailable = fields.Float()

    def _prepare_procurement_from_move(self):
        res = super(StockMove, self)._prepare_procurement_from_move()
        res["product_qty_unavailable"] = self.product_qty_unavailable
        return res
