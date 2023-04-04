# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.purchase_discount.models.purchase_order import (
    PurchaseOrderLine as PurchaseOrderLineBase,
)


class PurchaseOrderLine(PurchaseOrderLineBase):

    discount_global = fields.Float(
        default=lambda line: line.order_id.partner_id.supplier_discount
    )
    promotion_supplier = fields.Float(default=0.0)
    discount = fields.Float(compute="_compute_discount", readonly=False, store=True)

    @api.model
    def _apply_value_from_seller(self, seller):
        res = super()._apply_value_from_seller(seller)
        self.discount_global = self.partner_id.supplier_discount
        self.promotion_supplier = seller.discount
        return res

    @api.depends("promotion_supplier", "discount_global")
    def _compute_discount(self):
        for rec in self:
            rec.discount = 100 - (
                (100 - rec.discount_global) * (100 - rec.promotion_supplier) / 100
            )
