# -*- coding: utf-8 -*-
# © 2017 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models, api, _


class ActivityBasedCosting(models.Model):
    _name = 'activity.based.costing'
    _rec_name = 'code'
    _order = 'rate'

    code = fields.Char(required=True)
    rate = fields.Integer(required=True)
    nbr_products = fields.Integer('Number of products',
                                  compute='_compute_nbr_products',
                                  readonly=True)
    nbr_products_prc = fields.Integer('Number of products in percent',
                                      compute='_compute_nbr_products',
                                      readonly=True,
                                      digits=(3, 2))

    _sql_constrains = [('unique_rate',
                        'UNIQUE(rate)',
                        _('The rate must be unique'))]

    @api.multi
    def _compute_nbr_products(self):
        nbr_products = self.env['product.product'].search_count([])

        for abc in self:
            nbr_products_rate = self.env['product.product']\
                .search_count([('abc_id', '=', abc.id)])

            abc.nbr_products = nbr_products_rate
            abc.nbr_products_prc = (100.0 / nbr_products) * nbr_products_rate
