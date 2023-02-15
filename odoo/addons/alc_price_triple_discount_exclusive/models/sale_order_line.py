# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.alc_pricelist_discount.models.sale_order_line import (
    SaleOrderLine as SaleOrderLineBase,
)


class SaleOrderLine(SaleOrderLineBase):
    def compute_supplier_promotion(self):
        res = super().compute_supplier_promotion()
        self.filtered("discount_item_id.exclusive").update({"discount2": 0})
        return res
