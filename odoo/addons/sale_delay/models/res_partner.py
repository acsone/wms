# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    max_delay_for_sale_order_creation = fields.Float(
        string="Max delay on sale order operation",
        digits=(3, 4),
        help="Used to compute if the processing of a sale order in"
        "the background takes too long. (0.5 is 30 minutes)",
    )
