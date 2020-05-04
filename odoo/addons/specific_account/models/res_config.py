# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountConfigSettings(models.TransientModel):
    _inherit = "account.config.settings"

    invoice_terms_conditions = fields.Text(
        related="company_id.invoice_terms_conditions",
        string="Invoice Terms and Conditions",
        translate=True,
    )
