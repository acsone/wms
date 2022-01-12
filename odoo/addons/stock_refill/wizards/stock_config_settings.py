# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools import ormcache


class StockConfigSettings(models.TransientModel):

    _inherit = "stock.config.settings"

    enable_reserve_on_putaway = fields.Boolean()

    @api.model
    @ormcache()
    def _is_reserve_on_putway_enabled(self):
        IrConfigParameter = self.env["ir.config_parameter"]
        return IrConfigParameter.get_param(
            "stock_refill.enable_reserve_on_putaway", "1"
        ).lower() in ["true", "1", "t", "y", "yes"]

    @api.model
    def default_get(self, _fields):
        res = super(StockConfigSettings, self).default_get(_fields)
        if "enable_reserve_on_putaway" in _fields or not _fields:
            res["enable_reserve_on_putaway"] = self._is_reserve_on_putway_enabled()
        return res

    @api.multi
    def set_enable_reserve_on_putaway(self):
        self.ensure_one()

        self.env["ir.config_parameter"].set_param(
            "stock_refill.enable_reserve_on_putaway",
            self.enable_reserve_on_putaway or "false",
        )
