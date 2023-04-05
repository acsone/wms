# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.stock.models.stock_move import StockMove as StockMoveBase


class StockMove(StockMoveBase):

    # This is done to change the order of stock move when grouping - pivot, reports, ...
    date = fields.Datetime(group_operator="min")
