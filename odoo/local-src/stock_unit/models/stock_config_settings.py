# -*- coding: utf-8 -*-
# Copyright 2018 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class StockConfigSettings(models.TransientModel):
    _inherit = 'stock.config.settings'

    reservation_unit_pallet_factor = fields.Float('Factor for pallets')
    reservation_unit_box_factor = fields.Float('Factor for boxes')
    reservation_unit_wrap_factor = fields.Float('Factor for shrink wrap')
    reservation_unit_min_quantity = fields.Float('Minimum quantity')

    @api.model
    def default_get(self, fields):
        res = super(StockConfigSettings, self).default_get(fields)
        config_param = self.env['ir.config_parameter']

        if 'reservation_unit_pallet_factor' in fields or not fields:
            factor = float(config_param.get_param(
                'stock.reservation_unit_pallet_factor', 1))
            res['reservation_unit_pallet_factor'] = factor

        if 'reservation_unit_box_factor' in fields or not fields:
            factor = float(config_param.get_param(
                'stock.reservation_unit_box_factor', 1))
            res['reservation_unit_box_factor'] = factor

        if 'reservation_unit_wrap_factor' in fields or not fields:
            factor = float(config_param.get_param(
                'stock.reservation_unit_wrao_factor', 1))
            res['reservation_unit_wrap_factor'] = factor

        if 'reservation_unit_min_quantity' in fields or not fields:
            factor = float(config_param.get_param(
                'stock.reservation_unit_min_quantity_factor', 0))
            res['reservation_unit_min_quantity'] = factor

        return res
