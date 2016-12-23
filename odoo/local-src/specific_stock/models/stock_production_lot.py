# -*- coding: utf-8 -*-
# © 2016 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    removal_date = fields.Datetime(
        required=True,
    )

    # Cancel defaults values from `product_expiry` module
    _defaults = {
        'life_date': None,
        'use_date': None,
        'removal_date': None,
        'alert_date': None,
    }

    @api.model
    def create(self, vals):
        new_vals = vals.copy()
        if 'removal_date' not in vals.keys():
            context = self.env.context or {}
            if context.get('default_removal_date_allowed'):
                new_vals['removal_date'] = fields.datetime.now()
        return super(StockProductionLot, self).create(new_vals)

    @api.onchange('product_id')
    def _onchange_product(self):
        # Override the product_expiry module method
        # Do nothing : on Alcyon, the removal_date is entered by user
        # and is not computed with production lot created date
        pass
