# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class StockConfig(models.TransientModel):
    _inherit = 'stock.config.settings'

    production_lot_base_date = fields.Selection(
        selection='_selection_production_lot_base_date',
        string='Base date for compute expiration dates',
    )

    @api.model
    def _selection_production_lot_base_date(self):
        return [
            ('use', _('Use date')),
            ('life', _('Expiration date')),
            ('alert', _('Alert date')),
            ('removal', _('Removal date')),
        ]

    @api.model
    def get_default_production_lot_base_date(self, fields):
        icp = self.env['ir.config_parameter']
        return {
            'production_lot_base_date': icp.get_param(
                'stock_production_lot_expired_dates.production_lot_base_date',
                None,
            )
        }

    @api.multi
    def set_production_lot_base_date(self):
        self.env['ir.config_parameter'].set_param(
            'stock_production_lot_expired_dates.production_lot_base_date',
            self.production_lot_base_date,
        )
