# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.partner_invoicing_mode.models.sale_order import (
    SaleOrder as SaleOrderBase,
)


class SaleOrder(SaleOrderBase):
    def _get_generated_invoices(self, partition):
        invoices = self.env["account.move"]
        to_invoice = self.order_line.filtered(lambda line: line.qty_to_invoice > 0)
        to_refund = self.order_line.filtered(lambda line: line.qty_to_invoice < 0)
        # Create all the invoices
        if to_invoice:
            invoices |= self._create_invoices(grouped=partition, final=False)
        # Create all the refunds
        if to_refund:
            invoices |= self._create_invoices(grouped=partition, final=True)
        return invoices
