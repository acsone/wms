# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.product.models.product_template import (
    ProductTemplate as ProductTemplateBase,
)

from .animal_species import AnimalSpecies


class ProductTemplate(ProductTemplateBase):

    species_id = fields.Many2one[AnimalSpecies](string="Main Species")
    species_ids = fields.Many2many[AnimalSpecies](string="Species")
