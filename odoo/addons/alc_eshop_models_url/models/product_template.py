# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_product_url.models.product_template import (
    ProductTemplate as ProductTemplateBase,
)


class ProductTemplate(ProductTemplateBase):
    def _generate_url_key(self, referential, lang):
        url_key = super()._generate_url_key(referential, lang)
        return f"p/{url_key}"
