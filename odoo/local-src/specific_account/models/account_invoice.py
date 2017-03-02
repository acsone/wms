# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    supplier_invoice_number = fields.Char('Vendor reference', copy=False)

    _sql_constraints = [
        ('unique_invoice_number_by_supplier',
         'unique (partner_id,supplier_invoice_number)',
         'The supplier invoice number must be unique by supplier')
    ]
