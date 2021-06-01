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
    def _check_barcode(self):
        for rec in self:
            if rec.barcode != self._sanitize_name_for_barcode(rec.name):
                raise ValidationError(
                    _("Barcode %s could only contains alphanumeric characters and '*'")
                    % rec.barcode
                )

    @api.model
    def create(self, vals):
        if "barcode" not in vals:
            vals["barcode"] = self._sanitize_name_for_barcode(vals["name"])
        return super(StockLocation, self).create(vals)

    @api.model
    def _sanitize_name_for_barcode(self, value):
        return re.sub("[^0-9a-zA-Z*]+", "", value)
