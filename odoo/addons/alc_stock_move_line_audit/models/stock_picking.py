# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields

from odoo.addons.stock.models import stock_picking


class StockPicking(stock_picking.Picking):

    date_done = fields.Datetime(index=True)
