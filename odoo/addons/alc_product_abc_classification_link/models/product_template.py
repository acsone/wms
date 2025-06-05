# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from odoo.addons.stock_storage_type_putaway_abc.models.stock_location import (
    ABC_SELECTION,
)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    abc_storage = fields.Selection(
        ABC_SELECTION,
        default="b",
        compute="_compute_abc_storage",
        store=True,
        readonly=True,
    )

    @api.depends("product_variant_ids", "product_variant_ids.abc_storage")
    def _compute_abc_storage(self):
        unique_variants = self.filtered(
            lambda template: len(template.product_variant_ids) == 1
        )
        for template in unique_variants:
            template.abc_storage = template.product_variant_ids.abc_storage
        for template in self - unique_variants:
            if len(set(template.product_variant_ids.mapped("abc_storage"))) == 1:
                template.abc_storage = template.product_variant_ids[0].abc_storage
            else:
                template.abc_storage = False
