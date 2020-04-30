# -*- coding: utf-8 -*-
# © 2017 Sylvain Van Hoof (Okia SPRL)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_price_on_labels = fields.Boolean('Display price on labels')
    no_labels_products = fields.Boolean(
        string="Do not print product labels",
        help="Customer does not need product labels",
    )
