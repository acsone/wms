# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountPaymentMode(models.Model):

    _inherit = "account.payment.mode"

    invoice_frequency = fields.Selection(
        [("10_days", "10 Days"), ("1_month", "1 Month")], string="Invoice frequency"
    )
    invoice_grouping = fields.Selection(
        [("all_at_once", "All at once"), ("by_delivery", "By delivery")],
        string="Invoice grouping",
    )
