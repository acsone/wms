# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class IrConfigParameter(models.Model):
    _inherit = 'ir.config_parameter'

    @api.model
    def _clear_geo_optimization_cache_config(self):
        settings = self.env["stock.config.settings"]
        settings.get_optimization_config.clear_cache(settings)

    @api.multi
    def write(self, vals):
        self._clear_geo_optimization_cache_config()
        return super(IrConfigParameter, self).write(vals)

    @api.multi
    def unlink(self):
        self._clear_geo_optimization_cache_config()
        return super(IrConfigParameter, self).unlink()
