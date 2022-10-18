# Copyright 2016 Sylvain Van Hoof <svh@sylvainvh.be>
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields

from odoo.addons.product.models.product_product import ProductProduct
from odoo.addons.product_expiry.models.production_lot import StockLot as StockLotBase


class StockLot(StockLotBase, extends=True):  # type: ignore

    product_id = fields.Many2one[ProductProduct](tracking=True)
    name = fields.Char(tracking=True)

    use_date = fields.Datetime(tracking=True)
    removal_date = fields.Datetime(tracking=True)
    expiration_date = fields.Datetime(tracking=True)
    alert_date = fields.Datetime(tracking=True)
