# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.tools import ormcache


class StockConfigSettings(models.TransientModel):

    _inherit = "stock.config.settings"

    max_delay_to_process_receipt = fields.Integer(
        default=5, help="Maximum delay to handle the receipt of goods."
    )

    @api.model
    @ormcache()
    def get_max_delay_to_process_receipt_config(self):
        IrConfigParameter = self.env["ir.config_parameter"]
        max_delay_to_process_receipt = int(
            IrConfigParameter.get_param("stock_grn.max_delay_to_process_receipt", "5")
        )
        return max_delay_to_process_receipt

    @api.model
    def default_get(self, fields):
        res = super(StockConfigSettings, self).default_get(fields)
        max_delay_to_process_receipt = self.get_max_delay_to_process_receipt_config()
        if "max_delay_to_process_receipt" in fields or not fields:
            res["max_delay_to_process_receipt"] = max_delay_to_process_receipt
        return res

    @api.multi
    def set_max_delay_to_process_receipt(self):
        self.ensure_one()

        self.env["ir.config_parameter"].set_param(
            "stock_grn.max_delay_to_process_receipt",
            self.max_delay_to_process_receipt or "5",
        )
