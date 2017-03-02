# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    supplier_invoice_number = fields.Char('Vendor reference', copy=False)

    _sql_constraints = [
        ('unique_invoice_number_by_supplier',
         'unique (partner_id,supplier_invoice_number)',
         'The supplier invoice number must be unique by supplier')
    ]

    @api.onchange('supplier_invoice_number')
    def onchange_supplier_invoice_number(self):
        """
        Set the reference with the supplier invoice number
        if the reference is empty
        and the reference type is "Free Communication"
        :return:
        """
        self.ensure_one()

        if not self.supplier_invoice_number:
            return

        if self.reference_type == 'none' and not self.reference:
            self.reference = self.supplier_invoice_number
