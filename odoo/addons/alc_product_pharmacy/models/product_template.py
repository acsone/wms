# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import re

from odoo import _, api, fields, models


class ProductTemplate(models.Model):

    _inherit = "product.template"

    cnk_code = fields.Char(string="CNK", copy=False)

    code_cti = fields.Char("Code CTI Extended")
    code_amm = fields.Char("AMM Number")

    veterinary_only = fields.Boolean(string="Veterinary only")
    pharmacy_only = fields.Boolean("Only Pharmacies?")
    belgium_only = fields.Boolean(string="Belgium only")

    _sql_constraints = [
        (
            "uniq_cnk_code",
            "EXCLUDE (cnk_code WITH =) WHERE (cnk_code <> '' or cnk_code is not null)",
            _("This cnk_code already exists."),
        ),
    ]

    @api.model
    def create(self, vals):
        vals = ProductTemplate._remove_spaces_from_cnk(vals)
        return super(ProductTemplate, self).create(vals)

    @api.multi
    def write(self, vals):
        vals = ProductTemplate._remove_spaces_from_cnk(vals)
        return super(ProductTemplate, self).write(vals)

    @staticmethod
    def _remove_spaces_from_cnk(vals):
        if "cnk_code" in vals and vals["cnk_code"]:
            vals["cnk_code"] = re.sub(r"\s+", "", vals["cnk_code"])
        return vals
