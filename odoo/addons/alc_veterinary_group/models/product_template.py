# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.product.models.product_template import (
    ProductTemplate as ProductTemplateBase,
)

from .veterinary_group import VeterinaryGroup


class ProductTemplate(ProductTemplateBase):

    _inherit = "product.template"

    veterinary_group_ids = fields.Many2many[VeterinaryGroup](
        relation="product_template_veterinary_group_rel",
        column1="product_template_id",
        column2="veterinary_group_id",
        string="Veterinary Groups",
    )
