# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.tools import float_is_zero


class PurchaseOrder(models.Model):

    _inherit = "purchase.order"

    @api.multi
    def button_confirm(self):
        # remove empty lines from PO since it's not supported by ZOETIS
        digits = self.env["purchase.order.line"]._fields["product_qty"].digits
        self.mapped("order_line").filtered(
            lambda a: float_is_zero(a.product_qty, precision_digits=digits[1])
        ).unlink()
        return super(PurchaseOrder, self).button_confirm()
