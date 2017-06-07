# -*- coding: utf-8 -*-
# © 2017 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    volume = fields.Float(help='Volume in liter', digits=(12,3))

    length = fields.Float('Length', help='Length in cm')
    width = fields.Float('Width', help='Width in cm')
    depth = fields.Float('Depth', help='Depth in cm')

    @api.onchange('length', 'width', 'depth')
    def onchange_size(self):
        """
        Alcyon use centimeter for the length but use the liter for the volume.
        As a reminder: 1 cm³ = 0.001 liter and 1000 cm³ = 1 liter
        :return:
        """
        for product in self:
            volume_in_cm3 = product.length * product.width * product.depth
            volume_in_liter = volume_in_cm3 / 1000
            product.volume = volume_in_liter


    @api.model
    def get_default_state_id(self):
        """
        I need to do this check because the "default" for the state_id
        can be call before data are loaded
        """
        state_active = \
            self.env.ref('specific_purchase.product_state_active', False)

        if state_active:
            return state_active.id

    date_out_of_stock_expected = fields.Datetime('Expected out of stock date')
    state_id = fields.Many2one(
        'product.state',
        string='State',
        default=get_default_state_id
    )


class ProductState(models.Model):
    _name = 'product.state'
    _order = 'sequence'

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer()
