# -*- coding: utf-8 -*-
# © 2017 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    supplier_discount = fields.Float('Supplier discount %')

    purchase_manager_id = fields.Many2one(
        comodel_name='res.users',
        string='Purchase manager',
    )

    substitute_purchase_manager_id = fields.Many2one(
        comodel_name='res.users',
        string='Substitute purchase manager',
    )
    delivery_lead_time = fields.Integer('Delivery lead time')
