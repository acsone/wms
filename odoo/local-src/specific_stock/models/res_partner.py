# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_sale_back_order_accepted = fields.Boolean(
        string='Sale back order accepted',
        default=True,
    )
    is_purchase_back_order_accepted = fields.Boolean(
        string='Purchase back order accepted',
    )
