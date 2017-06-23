# -*- coding: utf-8 -*-
# © 2017 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    supplier_discount = fields.Float('Supplier discount %')
    is_back_order_accepted = fields.Boolean('Back order accepted')

    supplier_responsible_id = fields.Many2one(
        comodel_name='res.users',
        string='Supplier responsible',
    )

    supplier_substitute_responsible_id = fields.Many2one(
        comodel_name='res.users',
        string='Supplier substitute responsible',
    )
