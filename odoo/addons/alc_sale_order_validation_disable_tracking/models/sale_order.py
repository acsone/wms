# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.sale.models.sale_order import SaleOrder as SaleOrderBase


class SaleOrder(SaleOrderBase):
    def action_confirm(self):

        # Disable tracking
        result = super(
            SaleOrder, self.with_context(tracking_disable=True)
        ).action_confirm()

        # Post the message "Quotation confirmed"
        message = self.env.ref("sale.mt_order_confirmed")
        for so in self:
            so.message_post(body=message.description)
        return result
