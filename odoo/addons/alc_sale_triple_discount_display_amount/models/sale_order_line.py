# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools import float_compare


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    discount_total = fields.Monetary(
        compute="_compute_discount_total",
    )
    price_total_no_discount = fields.Monetary(
        compute="_compute_discount_total",
    )

    def _update_discount_display_fields(self):
        for line in self:
            price_total_no_discount = 0.0
            discount_total = 0.0
            if not line.discount and not line.discount2 and not line.discount3:
                price_total_no_discount = line.price_total
            else:
                price = line.price_unit
                taxes = line.tax_id.compute_all(
                    price,
                    line.order_id.currency_id,
                    line.product_uom_qty,
                    product=line.product_id,
                    partner=line.order_id.partner_shipping_id,
                )

                price_total_no_discount = taxes["total_included"]
                discount_total = price_total_no_discount - line.price_total
            currency = line.order_id.currency_id
            if float_compare(
                line.discount_total,
                discount_total,
                precision_rounding=currency.rounding,
            ):
                line.discount_total = discount_total
            if float_compare(
                line.price_total_no_discount,
                price_total_no_discount,
                precision_rounding=currency.rounding,
            ):
                line.price_total_no_discount = price_total_no_discount

    @api.depends(
        "discount",
        "discount2",
        "discount3",
        "price_total",
        "product_uom_qty",
        "product_id",
        "tax_id",
        "price_unit",
        "order_id.currency_id",
        "order_id.partner_shipping_id",
    )
    def _compute_discount_total(self):
        self._update_discount_display_fields()
