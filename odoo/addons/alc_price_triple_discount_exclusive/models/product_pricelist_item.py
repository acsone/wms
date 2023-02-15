# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.product.models.product_pricelist_item import PricelistItem


class ProductPricelistItem(PricelistItem):

    exclusive = fields.Boolean(
        string="Exclusive", default=False, help="Only applied for discount items."
    )
