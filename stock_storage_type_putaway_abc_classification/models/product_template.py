# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.fields import first

from odoo.addons.stock_storage_type_putaway_abc.models.stock_location import (
    ABC_SELECTION,
)


class ProductTemplate(models.Model):

    _inherit = "product.template"

    abc_storage = fields.Selection(
        ABC_SELECTION, compute="_compute_abc_storage", store=True, index=True
    )

    @api.depends(
        "abc_classification_product_level_ids",
        "abc_classification_product_level_ids.level_id",
    )
    def _compute_abc_storage(self):
        for rec in self:
            level = (
                first(rec.abc_classification_product_level_ids)
                if rec.abc_classification_product_level_ids
                else rec.abc_classification_product_level_ids
            )
            rec.abc_storage = level.level_id.name
