# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import re

from odoo import _, api, fields

from odoo.addons.product.models.product_template import (
    ProductTemplate as ProductTemplateBase,
)


class ProductTemplate(ProductTemplateBase):

    cnk_code = fields.Char(string="CNK", copy=False)

    code_cti = fields.Char("Code CTI Extended", copy=False)
    code_amm = fields.Char("AMM Number")

    veterinary_only = fields.Boolean(string="Veterinary only")
    belgium_only = fields.Boolean(string="Belgium only")

    is_human = fields.Boolean(
        string="Human",
        compute="_compute_category_attributes",
        store=True,
    )
    is_colis_souverain = fields.Boolean(
        string="Colis",
        compute="_compute_category_attributes",
        store=True,
    )
    is_equipment = fields.Boolean(
        string="Equipment",
        compute="_compute_category_attributes",
        store=True,
    )
    is_meds = fields.Boolean(
        string="Medicine",
        compute="_compute_category_attributes",
        store=True,
    )
    is_narcotic_reg = fields.Boolean(
        string="Narcotics (Regular)",
        compute="_compute_category_attributes",
        store=True,
    )
    is_narcotic_vet = fields.Boolean(
        string="Narcotics (Veterinary)",
        compute="_compute_category_attributes",
        store=True,
    )
    is_psychotropic = fields.Boolean(
        string="Psychotropic",
        compute="_compute_category_attributes",
        store=True,
    )
    is_pharmaceutical = fields.Boolean(
        string="Parapharmaceutical",
        compute="_compute_category_attributes",
        store=True,
    )
    is_import = fields.Boolean(
        string="Importation",
        compute="_compute_category_attributes",
        store=True,
    )
    is_vt_be = fields.Boolean(
        string="Belgian Veterinaries",
        compute="_compute_category_attributes",
        store=True,
    )

    _sql_constraints = [
        (
            "uniq_cnk_code",
            "EXCLUDE (cnk_code WITH =) WHERE (cnk_code <> '' or cnk_code is not null)",
            _("This cnk_code already exists."),
        ),
        (
            "uniq_code_cti",
            "EXCLUDE (code_cti WITH =) WHERE (code_cti <> '' or code_cti is not null)",
            _("This CTI extended code already exists."),
        ),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        vals_list = [
            ProductTemplate._remove_spaces_from_cnk(vals) for vals in vals_list
        ]
        return super().create(vals_list)

    def write(self, vals):
        vals = ProductTemplate._remove_spaces_from_cnk(vals)
        return super().write(vals)

    @staticmethod
    def _remove_spaces_from_cnk(vals):
        if "cnk_code" in vals and vals["cnk_code"]:
            vals["cnk_code"] = re.sub(r"\s+", "", vals["cnk_code"])
        return vals

    @api.model
    def _get_category_attributes(self):
        return {
            "is_meds": "alc_product_category_data.product_categ_medoc",
            "is_equipment": "alc_product_category_data.product_categ_materiel",
            "is_vt_be": "alc_product_category_data.product_categ_vet_belges",
            "is_human": "alc_product_category_data.product_categ_humain",
            "is_colis_souverain": "alc_product_category_data.product_categ_colis_souverain",
            "is_narcotic_reg": "alc_product_category_data.product_categ_stupefiant",
            "is_narcotic_vet": "alc_product_category_data.product_categ_stupefiant_vet",
            "is_psychotropic": "alc_product_category_data.product_categ_psychotropes_25",
            "is_pharmaceutical": "alc_product_category_data.product_categ_parapharmacie",
            "is_import": "alc_product_category_data.product_categ_importation",
        }

    @api.depends("categ_id")
    def _compute_category_attributes(self):
        for field, root_xmlid in self._get_category_attributes().items():
            self._compute_business_unit_property(field, root_xmlid)
