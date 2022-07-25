# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def compute_supplier_promotion(self):
        res = super(SaleOrderLine, self).compute_supplier_promotion()
        for line in self:
            if line.discount_item_id.exclusive:
                line.discount2 = 0
        return res
