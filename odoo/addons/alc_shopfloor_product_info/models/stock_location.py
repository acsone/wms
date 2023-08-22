# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.stock.models.stock_location import Location


class StockLocation(Location):

    display_in_shopfloor_product_info = fields.Boolean(default=True)
