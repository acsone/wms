# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):

    _inherit = "sale.order"

    def action_confirm_cart(self):
        for record in self:
            for line in record.order_line:
                if line.product_id.shop_order_mode == "quotation_only":
                    raise ValidationError(
                        _(
                            "You can not confirm this cart because some of the products are only available on quotation."
                        )
                    )
        return super().action_confirm_cart()
