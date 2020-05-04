# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.onchange("purchase_id")
    def purchase_order_change(self):
        """Overloaded to change the way PO lines are invoiced based on the
        'prepayment' field.

            - if PO premayment is True, we invoice all the ordered qty
            - if not, we invoice only the current received qty of PO lines
        """
        # If no prepayment, invoice receive qty from PO lines
        # NOTE: all products are configured to be invoiced based on the
        # received qty (purchase_method == 'receive')
        if not self.purchase_id.prepayment:
            res = super(AccountInvoice, self).purchase_order_change()
            # We remove lines with no quantity
            invoice_lines_to_keep = self.invoice_line_ids.filtered(lambda l: l.quantity)
            self.invoice_line_ids = invoice_lines_to_keep
            return res
        # If prepayment, invoice all ordered  qty
        if not self.purchase_id:
            return {}
        if not self.partner_id:
            self.partner_id = self.purchase_id.partner_id.id
        lines_to_invoice = self.purchase_id.order_line - self.invoice_line_ids.mapped(
            "purchase_line_id"
        )
        new_lines = self.env["account.invoice.line"]
        for line in lines_to_invoice:
            # Temporarily set the invoicing method of the product to
            # generate the invoice line based on the ordered qty
            orig_method = line.product_id.purchase_method
            line.product_id.purchase_method = "purchase"
            data = self._prepare_invoice_line_from_po_line(line)
            new_line = new_lines.new(data)
            new_line._set_additional_fields(self)
            new_lines += new_line
            # Restore the invoicing method
            line.product_id.purchase_method = orig_method
        self.invoice_line_ids += new_lines
        self.purchase_id = False
        return {}
