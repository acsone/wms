# -*- coding: utf-8 -*-
# © 2016 Sylvain Van Hoof
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import models, fields, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    journal_id = fields.Many2one(default='_default_journal')

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
        """
        The user should insert himself the journal
        :return: Return an empty account.journal browse record set
        """
        return self.env['account.journal']

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        """
        We don't want to update the journal when the user change the partner_id
        :return: The result of the onchange_partner_id
        """
        self.ensure_one()

        current_journal = self.journal_id

        result = super(AccountInvoice, self)._onchange_partner_id()
        if self.journal_id != current_journal:
            self.journal_id = current_journal

        return result
