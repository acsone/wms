# -*- coding: utf-8 -*-
# Copyright 2018 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    invoice_frequency = fields.Selection(
        [('10_days', '10 Days'),
         ('1_month', '1 Month')],
        string='Invoice frequency',
        default='10_days',
    )
    invoice_type = fields.Selection(
        [('in_one_time', 'In one time'),
         ('by_delivery', 'By delivery')],
        string='Invoice type',
        default='in_one_time'
    )
