# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA, Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models, api


class StockConfigSettings(models.TransientModel):
    _inherit = 'stock.config.settings'

    price_limit_for_inventory = fields.Float('Price limit for inventory')
    nbr_open_days = fields.Integer('Number of open days')

    @api.model
    def default_get(self, fields):
        res = super(StockConfigSettings, self).default_get(fields)

        config_param = self.env['ir.config_parameter']
        if 'price_limit_for_inventory' in fields or not fields:
            price = float(config_param
                          .get_param('stock.price_limit_for_inventory', 0))
            res['price_limit_for_inventory'] = price
        if 'nbr_open_days' in fields or not fields:
            days = int(config_param.get_param('stock.nbr_open_days', 0))
            res['nbr_open_days'] = days

        return res

    @api.multi
    def set_price_limit_for_inventory(self):
        self.ensure_one()

        self.env['ir.config_parameter']\
            .set_param('stock.price_limit_for_inventory',
                       self.price_limit_for_inventory or '0')

    @api.multi
    def set_nbr_open_days(self):
        self.ensure_one()

        self.env['ir.config_parameter'] \
            .set_param('stock.nbr_open_days',
                       self.nbr_open_days or '0')
