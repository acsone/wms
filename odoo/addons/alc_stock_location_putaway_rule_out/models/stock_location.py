# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.stock.models.product_strategy import StockPutawayRule
from odoo.addons.stock.models.stock_location import Location


class StockLocation(Location):

    putaway_rule_out_ids = fields.One2many[StockPutawayRule](
        inverse_name="location_out_id",
        string="Putaway Out Rules",
        help="putaway rules having this location as destination",
    )
