# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockMove(models.Model):

    _inherit = "stock.move"

    # a pocking can be assigned to a delivery round only if
    # we've at lease one stock.move with delivery_requires_other_lines not set
    # for the same partner for all the pickings candidate to the delivery
    delivery_requires_other_lines = fields.Boolean(default=False)

    def _prepare_procurement_from_move(self):
        res = super(StockMove, self)._prepare_procurement_from_move()
        res["delivery_requires_other_lines"] = self.delivery_requires_other_lines
        return res
