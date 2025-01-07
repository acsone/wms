# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.sale_order_blanket_order.models.sale_order import (
    SaleOrder as SaleOrderBase,
)


class SaleOrder(SaleOrderBase):
    def _get_default_call_off_order_values(self, blanket_order_id):
        vals = super()._get_default_call_off_order_values(blanket_order_id)
        if self.sale_channel_id:
            vals["sale_channel_id"] = self.sale_channel_id.id
        return vals
