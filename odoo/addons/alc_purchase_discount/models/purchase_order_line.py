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
    def _get_discount(self, discount_global, promotion_supplier):
        return 100 - ((100 - discount_global) * (100 - promotion_supplier) / 100)

    @api.depends("promotion_supplier", "discount_global")
    def _compute_discount(self):
        for rec in self:
            rec.discount = rec._get_discount(
                rec.discount_global, rec.promotion_supplier
            )

    @api.model
    def _apply_value_from_seller(self, seller):
        res = super()._apply_value_from_seller(seller)
        self.discount_global = self.partner_id.supplier_discount
        self.promotion_supplier = seller.discount
        return res

    @api.model
    def _prepare_purchase_order_line(
        self, product_id, product_qty, product_uom, company_id, supplier, po
    ):
        values = super()._prepare_purchase_order_line(
            product_id, product_qty, product_uom, company_id, supplier, po
        )
        values.update(
            {
                "discount": self._get_discount(
                    supplier.partner_id.supplier_discount,
                    values.get("promotion_supplier", 0),
                ),
                "discount_global": supplier.partner_id.supplier_discount,
            }
        )
        return values

    def _prepare_purchase_order_line_from_seller(self, seller):
        values = super()._prepare_purchase_order_line_from_seller(seller)
        values.update({"promotion_supplier": seller.discount})
        return values

    @api.depends("date_order")
    def _compute_price_unit_and_date_planned_and_name(self):
        res = super()._compute_price_unit_and_date_planned_and_name()
        for rec in self:
            if not rec.product_id or rec.invoice_lines or not rec.company_id:
                continue
            if rec.date_order:
                date = rec.date_order.date()
            params = {"order_id": rec.order_id}
            seller = rec.product_id._select_seller(
                partner_id=rec.partner_id,
                quantity=rec.product_qty,
                date=date,
                uom_id=rec.product_uom,
                params=params,
            )
            rec._apply_value_from_seller(seller)
        return res
