# -*- coding: utf-8 -*-
# Copyright 2016-2018 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    @api.model
    def _get_product_expired_times(self, product):
        return {
            'life_time': product.life_time,
            'use_time': product.use_time,
            'removal_time': product.removal_time,
            'alert_time': product.alert_time,
        }

    @api.multi
    def _apply_onchange_interval_date(self, from_field):
        self.ensure_one()
        base_date = self.env['ir.config_parameter'].get_param(
            'stock_production_lot_expired_dates.production_lot_base_date'
        )
        if self.product_id and base_date == from_field:
            if getattr(self, from_field + '_date'):
                to_fields = ['alert', 'life', 'removal', 'use']
                to_fields.remove(from_field)
                times = self._get_product_expired_times(self.product_id)
                from_time = times[from_field + '_time']
                from_date = fields.Datetime.from_string(
                    getattr(self, from_field + '_date')
                )
                values = {}
                for index in [0, 1, 2]:
                    if times[to_fields[index] + '_time']:
                        days = from_time - times[to_fields[index] + '_time']
                        values[
                            to_fields[index] + '_date'
                        ] = from_date - relativedelta(days=days)
                if values:
                    self.update(values)

    @api.onchange('removal_date')
    def onchange_removal_date(self):
        self._apply_onchange_interval_date('removal')

    @api.onchange('alert_date')
    def onchange_alert_date(self):
        self._apply_onchange_interval_date('alert')

    @api.onchange('life_date')
    def onchange_life_date(self):
        self._apply_onchange_interval_date('life')

    @api.onchange('use_date')
    def onchange_use_date(self):
        self._apply_onchange_interval_date('use')
