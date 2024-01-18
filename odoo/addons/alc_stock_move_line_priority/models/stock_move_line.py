# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.stock.models import stock_move_line


class StockMoveLine(stock_move_line.StockMoveLine):

    priority = fields.Selection(
        related="move_id.priority",
        readonly=True,
        store=True,
    )
