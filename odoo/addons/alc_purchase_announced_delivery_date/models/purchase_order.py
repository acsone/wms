# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.purchase_stock.models import purchase


class PurchaseOrder(purchase.PurchaseOrder):
    def button_confirm(self):
        for po in self:
            for line in po.order_line:
                line.date_announced = po.date_planned
        return super().button_confirm()
