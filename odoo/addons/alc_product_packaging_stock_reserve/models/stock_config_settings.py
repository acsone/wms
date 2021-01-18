# -*- coding: utf-8 -*-
# Copyright 2018 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockConfigSettings(models.TransientModel):
    _inherit = "stock.config.settings"

    reservation_unit_min_quantity = fields.Float("Minimum quantity")

    @api.model
    def default_get(self, _fields):
        res = super(StockConfigSettings, self).default_get(_fields)
        config_param = self.env["ir.config_parameter"]

        if "reservation_unit_min_quantity" in _fields or not _fields:
            factor = float(
                config_param.get_param("stock.reservation_unit_min_quantity_factor", 0)
            )
            res["reservation_unit_min_quantity"] = factor

        return res
