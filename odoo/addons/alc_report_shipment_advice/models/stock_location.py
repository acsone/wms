# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.stock.models.stock_location import Location


class StockLocation(Location):

    show_in_shipment_advice_report = fields.Boolean()
