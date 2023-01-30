# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.alc_product_pharmacy.models import (
    ProductTemplate as ProductTemplateBase,
)
from odoo.addons.base_sparse_field.models.fields import Serialized

from .product_partner_type import ProductPartnerType


class ProductTemplate(ProductTemplateBase, ProductPartnerType):

    _name = "product.template"

    allowed_partner_types = fields.Char(
        string="Allowed Partner Types",
        store=True,
        compute="_compute_allowed_partner_types",
        help="Technical field. Stores all partner types allowed to access the product.",
    )

    allowed_partner_types_list = Serialized(
        string="Allowed Partner Types List",
        compute="_compute_allowed_partner_types_list",
        help="Technical field. Stores all partner types allowed to access the product.",
    )

    @api.depends("categ_id")
    def _compute_allowed_partner_types_list(self):
        for product in self:
            product.allowed_partner_types_list = list(
                product.get_allowed_partner_types()
            )

    @api.depends("categ_id")
    def _compute_allowed_partner_types(self):
        for product in self:
            allowed_partner_types = product.get_allowed_partner_types()
            product.allowed_partner_types = ",".join(allowed_partner_types)
