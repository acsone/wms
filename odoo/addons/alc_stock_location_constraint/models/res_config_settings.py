# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    alc_stock_location_constraint = fields.Boolean(
        string="Stock Location Constraints",
        help="Check this if you want the stock locations to be unique across several parameters:"
        "Location Zone, Corridor, Rack, Level, Position(X, Y, Z)",
        config_parameter="alc_stock_location_constraint.stock_location_constraint",
    )
