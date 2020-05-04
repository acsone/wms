# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class AccountTax(models.Model):
    _inherit = "account.tax"

    esb_ref = fields.Char(string="Reference for ESB", copy=False)
    contrib_sku = fields.Char(string="Contribution SKU", copy=False)
