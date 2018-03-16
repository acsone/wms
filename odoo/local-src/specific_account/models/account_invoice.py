# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def _onchange_partner_id(self):
        """ Fix puchase module that override journal for unknown reason """
        journal = self.journal_id
        res = super(AccountInvoice, self)._onchange_partner_id()
        if self.journal_id != journal:
            self.journal_id = journal
        return res

    @api.onchange('partner_id')
    def _onchange_intrastat_country(self):
        self.intrastat_country_id = self.partner_id.country_id
