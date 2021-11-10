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

    human_only = fields.Boolean(compute="_compute_human_only", store=True)

    _sql_constraints = [
        (
            "uniq_cnk_code",
            "EXCLUDE (cnk_code WITH =) WHERE (cnk_code <> '' or cnk_code is not null)",
            _("This cnk_code already exists."),
        ),
        (
            "uniq_code_amm",
            "EXCLUDE (code_amm WITH =) WHERE (code_amm <> '' or code_amm is not null)",
            _("This AMM number already exists."),
        ),
        (
            "uniq_code_cti",
            "EXCLUDE (code_cti WITH =) WHERE (code_cti <> '' or code_cti is not null)",
            _("This CTI extended code already exists."),
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

    @api.depends("categ_id")
    def _compute_human_only(self):
        root_xmlid = "specific_data.product_categ_humain"
        self._compute_business_unit_property("human_only", root_xmlid)
