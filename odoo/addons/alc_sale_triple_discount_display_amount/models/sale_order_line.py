# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.sale_discount_display_amount.models.sale_order_line import (
    SaleOrderLine as SaleOrderLineBase,
)


class SaleOrderLine(SaleOrderLineBase):
    def _has_discount(self):
        self.ensure_one()
        currency = (
            self.currency_id if self.currency_id else self.env.company.currency_id
        )
        return (
            super()._has_discount()
            or not currency.is_zero(self.discount2)
            or not currency.is_zero(self.discount3)
        )
