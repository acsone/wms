# -*- coding: utf-8 -*-
# © 2016 Sylvain Van Hoof
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import models, fields, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    JOURNAL_BY_INVOICE_TYPE = {
        'out_invoice': 'sale',
        'in_invoice': 'purchase',
        'out_refund': 'sale_refund',
        'in_refund': 'purchase_refund',
    }

    @api.multi
    @api.onchange('type')
    def onchange_type(self):
        self.ensure_one()

        if not self.type:
            return

        journal_type = self.JOURNAL_BY_INVOICE_TYPE.get(self.type)
        if journal_type:
            journal_domain = [('type', '=', journal_type)]
        else:
            journal_domain = []

        return {
            'domain': {
                'journal_id': journal_domain,
            },
        }

    @api.model
    def _default_journal(self):
        if self._context.get('default_journal_id', False):
            return self.env['account.journal'].browse(
                self._context.get('default_journal_id'))
        inv_type = self._context.get('type', 'out_invoice')
        inv_types = inv_type if isinstance(inv_type, list) else [inv_type]
        company_id = self._context.get('company_id',
                                       self.env.user.company_id.id)
        domain = [
            ('type', 'in', filter(
                None, map(self.JOURNAL_BY_INVOICE_TYPE.get, inv_types))),
            ('company_id', '=', company_id),
        ]
        return self.env['account.journal'].search(domain, limit=1)

    journal_id = fields.Many2one(default=_default_journal)
