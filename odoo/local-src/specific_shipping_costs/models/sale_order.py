# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    used_for_delivery_fee = fields.Boolean(
        'Has been used for delivery fee calculation'
    )
