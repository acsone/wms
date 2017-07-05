# -*- coding: utf-8 -*-
# © 2017 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    volume = fields.Float(string='Volume (liter)',
                          help='Volume in liter',
                          digits=(12, 3))

    length = fields.Float('Length (cm)', help='Length in cm')
    width = fields.Float('Width (cm)', help='Width in cm')
    depth = fields.Float('Depth (cm)', help='Depth in cm')
    supplier_id = fields.Many2one('res.partner',
                                  string='Vendor',
                                  readonly=True,
                                  compute='_compute_supplier_id',
                                  store=True)

    @api.depends('seller_ids')
    def _compute_supplier_id(self):
        """
        Compute the supplier for each product.
        Alcyon cannot have more than one supplier per product.
        This field will be used by filters
        :return:
        """
        for product in self:
            sellers = product.seller_ids.mapped('name')
            if len(sellers) == 1:
                product.supplier_id = sellers.id
            else:
                product.supplier_id = None

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

    date_out_of_stock_expected = fields.Datetime('Expected out of stock date')
    state_id = fields.Many2one(
        'product.state',
        string='State',
    )


class ProductState(models.Model):
    _name = 'product.state'
    _order = 'sequence'

    name = fields.Char(required=True, translate=True)
    code = fields.Char(required=True)
    sequence = fields.Integer()
