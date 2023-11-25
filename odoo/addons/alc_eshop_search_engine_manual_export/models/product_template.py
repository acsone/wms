# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_search_engine.models.product_template import (
    ProductTemplate as ProductTemplateBase,
)


class ProductTemplate(ProductTemplateBase):
    def shopinvader_manual_export(self):
        self.product_variant_ids.shopinvader_manual_export()
