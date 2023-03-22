# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.product.models import product_product
from odoo.addons.stock.models.stock_lot import StockLot


class ProductProduct(product_product.ProductProduct):

    lot_ids = fields.One2many[StockLot](
        string="Lots",
        inverse_name="product_id",
        readonly=True,
    )
