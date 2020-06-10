# -*- coding: utf-8 -*-
# Copyright 2018 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    invoice_frequency = fields.Selection(
        [("10_days", "10 Days"), ("1_month", "1 Month")],
        string="Invoice frequency",
        default="10_days",
    )
    invoice_grouping = fields.Selection(
        [("all_at_once", "All at once"), ("by_delivery", "By delivery")],
        string="Invoice grouping",
        default="all_at_once",
    )
