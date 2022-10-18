# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    def _check_delivery_requires_other_lines(self):
        self.ensure_one()
        if self.product_qty_unavailable > 0:
            return True
        return super(SaleOrderLine, self)._check_delivery_requires_other_lines()
