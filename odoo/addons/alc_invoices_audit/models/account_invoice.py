# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountInvoice(models.Model):

    _inherit = "account.invoice"

    customer_call_name = fields.Char(related="partner_id.call_name", readonly=True)
    invoice_frequency = fields.Selection(
        related="partner_id.invoice_frequency", readonly=True
    )
