# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class RoundTemplate(models.Model):

    _inherit = "round.template"

    geo_optimization_enabled = fields.Boolean(
        "Enable geo optimization", default=lambda a: a.get_optimization_config().enabled
    )

    @api.model
    def get_optimization_config(self):
        return self.env["stock.config.settings"].get_optimization_config()
