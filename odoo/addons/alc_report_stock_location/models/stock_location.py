from odoo import fields

from odoo.addons.stock.models.stock_location import Location


class StockLocation(Location):

    height = fields.Char()
