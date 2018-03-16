# -*- coding: utf-8 -*-
# © 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    reference = fields.Char('Payment Communication')
    supplier_invoice_number = fields.Char('Vendor Reference', copy=False)

    _sql_constraints = [
        ('unique_invoice_number_by_supplier',
         'unique (partner_id,supplier_invoice_number)',
         'The supplier invoice number must be unique by supplier')
    ]

    @api.onchange('supplier_invoice_number', 'reference_type')
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
        if not self.reference:
            self.reference = self.supplier_invoice_number

    @api.onchange('partner_id')
    def onchange_bba_partner(self):
        reference_type = 'none'
        if self.partner_id and (self.type == 'out_invoice'):
            reference_type = self.partner_id.out_inv_comm_type
        self.reference_type = reference_type or 'none'

    @api.onchange('reference_type')
    def onchange_bba_referencetype(self):
        reference = False
        if self.partner_id and (self.type == 'out_invoice'):
            if self.reference_type:
                reference = self.generate_bbacomm(
                    self.type, self.reference_type, self.partner_id.id,
                    '')['value']['reference']
        self.reference = reference
