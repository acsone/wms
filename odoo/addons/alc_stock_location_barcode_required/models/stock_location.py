# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import re

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockLocation(models.Model):

    _inherit = "stock.location"

    barcode = fields.Char(required=True, index=True)

    @api.constrains("barcode")
    def _onchange_name(self):
        for rec in self:
            if rec.barcode and not rec.barcode.isalnum():
                raise ValidationError(
                    _("Barcode %S could only contains alphanumeric characters")
                    % rec.barcode
                )

    @api.model
    def create(self, vals):
        if "barcode" not in vals:
            vals["barcode"] = re.sub("[^0-9a-zA-Z]+", "*", vals["name"])
        return super(StockLocation, self).create(vals)
