# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields

from odoo.addons.stock.models.stock_location import Location


class StockLocation(Location):

    # TODO: Remove this
    picking_zone_id = fields.Many2one[Location](
        string="ALC Stock Picking Zone",
        related="zone_location_id",
        help="This is a temporary field in order to smooth the barcode app migration",
    )
