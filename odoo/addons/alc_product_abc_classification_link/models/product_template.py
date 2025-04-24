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

    @api.depends("abc_classification_product_level_ids")
    def _compute_abc_storage(self):
        for template in self:
            template.abc_storage = (
                template.abc_classification_product_level_ids[0].level_id.name
                if template.abc_classification_product_level_ids
                else "b"
            )
