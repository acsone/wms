# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class IrConfigParameter(models.Model):
    _inherit = "ir.config_parameter"

    @api.model
    def _clear_is_reserve_on_putway_enabled_cache(self):
        settings = self.env["stock.config.settings"]
        settings._is_reserve_on_putway_enabled.clear_cache(settings)

    @api.multi
    def write(self, vals):
        self._clear_is_reserve_on_putway_enabled_cache()
        return super(IrConfigParameter, self).write(vals)

    @api.multi
    def unlink(self):
        self._clear_is_reserve_on_putway_enabled_cache()
        return super(IrConfigParameter, self).unlink()
