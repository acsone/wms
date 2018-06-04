# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_sale_back_order_accepted = fields.Boolean(
        string='Sale backorder accepted',
        default=True,
    )
    is_purchase_back_order_accepted = fields.Boolean(
        string='Purchase backorder accepted',
    )
