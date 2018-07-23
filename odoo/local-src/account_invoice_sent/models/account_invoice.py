# -*- coding: utf-8 -*-
# Copyright 2015-2018 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    # Allow to change value in 'open' state
    sent = fields.Boolean(
        readonly=True, states={'open': [('readonly', False)]})

    sending_method = fields.Selection(
        readonly=True,
        related="partner_id.invoice_sending_method",
        string="Sending Method")
