# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons.queue_job.job import job, related_action


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    @job(default_channel='root.invoice_validation')
    @related_action(action='related_action_open_invoice')
    def _job_validate_invoice(self, date_invoice):
        # Reload self as an invoice could have been deleted inbetween
        self = self.search([('id', 'in', self.ids)])
        if not self:
            return
        # Set date
        self.write({'date_invoice': date_invoice})
        # Validate invoice
        self.action_invoice_open()

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        """ Fix puchase module that override journal based on currency.
        On the screen, the journal is first selected, then the supplier
        and it's not expected to have the journal changed back automatically
        """
        journal = self.journal_id
        res = super(AccountInvoice, self)._onchange_partner_id()
        if self.journal_id != journal:
            self.journal_id = journal
        return res

    @api.onchange('partner_id')
    def _onchange_intrastat_country(self):
        self.intrastat_country_id = self.partner_id.country_id


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    invoice_state = fields.Selection(related='invoice_id.state', readonly=True)
