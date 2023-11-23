# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.connector_search_engine.models.se_index import SeIndex
from odoo.addons.shopinvader_search_engine.models.product_product import (
    ProductProduct as ProductProductBase,
)


class ProductProduct(ProductProductBase):
    def _get_image_url_key(self, index: SeIndex, field_name: str):
        # By default the display name is used as base name for the thumbnail
        # image. To ensure that the exsting thumbnails will be kept when
        # migrating from odoo 10 to odoo 16, we will use the name of the product
        # in place of the display name. The display name contains the default
        # code but when the thumbnail was created, the display_name of the template
        # was used which does not contain the default code. The name of the product
        # is equal to the display name of the template.
        self.ensure_one()
        return self.name
