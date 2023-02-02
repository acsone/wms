# Copyright 2018 Sylvain Van Hoof (Okia SPRL)
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.purchase.models.purchase import (
    PurchaseOrderLine as PurchaseOrderLineBase,
)


class PurchaseOrderLine(PurchaseOrderLineBase):

    is_additional_product = fields.Boolean(string="Additional product")

    def _compute_additional_products(self):
        for rec in self:
            rec._compute_additional_product()

    def _compute_additional_product(self):
        self.ensure_one()
        additional_product_qty = self.product_id._get_qty_additional_product(
            self.product_qty
        )
        if additional_product_qty:
            return self.copy(
                default=self._prepare_compute_additional_product_vals(
                    additional_product_qty
                )
            )
        return self.browse()

    def _prepare_compute_additional_product_vals(self, additional_product_qty):
        self.ensure_one()
        additional_product = self.product_id.additional_product_id
        # Set the language of the supplier
        additional_product_lang = additional_product.with_context(
            lang=self.partner_id.lang, partner_id=self.partner_id.id
        )
        return {
            "name": additional_product_lang.display_name,
            "order_id": self.order_id.id,
            "price_unit": 0,
            "product_id": additional_product.id,
            "product_uom": additional_product.uom_id.id,
            "product_qty": additional_product_qty,
            "is_additional_product": True,
        }
