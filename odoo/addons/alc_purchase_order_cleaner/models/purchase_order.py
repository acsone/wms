# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tools import float_is_zero

from odoo.addons.purchase.models import purchase


class PurchaseOrder(purchase.PurchaseOrder):
    def button_confirm(self):
        # remove empty lines from PO since it's not supported by ZOETIS
        digits = self.env["purchase.order.line"]._fields["product_qty"]._digits
        precision = self.env["decimal.precision"].precision_get(digits)
        self.mapped("order_line").filtered(
            lambda a: float_is_zero(a.product_qty, precision_digits=precision)
        ).unlink()
        return super().button_confirm()
