# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.product.models.product_template import (
    ProductTemplate as ProductTemplateBase,
)


class ProductTemplate(ProductTemplateBase):

    vt_groups = fields.Json(compute="_compute_vt_groups")

    @api.depends("veterinary_group_ids")
    def _compute_vt_groups(self):
        for product in self:
            product.vt_groups = {vg.id: vg.name for vg in product.veterinary_group_ids}
