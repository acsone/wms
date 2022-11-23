# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.product.models.product_template import ProductTemplate as TemplateBase
from odoo.addons.uom.models.uom_uom import UoM


class ProductTemplate(TemplateBase):

    volume_liter = fields.Float(
        related="product_variant_ids.volume_liter", readonly=True
    )
    dimensional_uom_id = fields.Many2one[UoM](
        readonly=True,
    )
