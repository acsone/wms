# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class IrModel(models.Model):

    _inherit = "ir.model"

    continuous_update = fields.Boolean(compute="_compute_continuous_update")

    @api.model
    def _get_continuous_models(self):
        return ["shopinvader.variant"]  # split and put in another module?

    @api.model
    def _compute_continuous_update(self):
        continuous_models = self._get_continuous_models()
        for model in self:
            model.continuous_update = model.model in continuous_models
