# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProcurementOrder(models.Model):

    _inherit = "procurement.order"
    product_qty_unavailable = fields.Float()

    def _get_stock_move_values(self):
        res = super(ProcurementOrder, self)._get_stock_move_values()
        res["product_qty_unavailable"] = self.product_qty_unavailable
        return res
