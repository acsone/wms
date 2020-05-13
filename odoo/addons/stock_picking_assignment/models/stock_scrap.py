# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockScrap(models.Model):

    _inherit = "stock.scrap"

    operator_id = fields.Many2one(
        "res.users",
        string="Operator",
        copy=False,
        track_visibility="onchange",
        default=lambda self: self._get_default_operator_id(),
    )

    @api.model
    def _get_default_operator_id(self):
        return self.env.user.id

    @api.model
    @api.returns("self", lambda value: value.id)
    def create(self, vals):
        if "operator_id" not in vals or not vals.get("operator_id"):
            vals["operator_id"] = self._get_default_operator_id()
        return super(StockScrap, self).create(vals)
