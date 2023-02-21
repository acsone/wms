# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.stock.models.stock_picking import PickingType


class StockPickingType(PickingType):

    allow_additional_product_on_reserved_qty = fields.Boolean(
        string="Allow Additional Product On Reserved Quantity"
    )
    no_backorder_for_additional_product = fields.Boolean(
        string="No Backorders for additional products"
    )
