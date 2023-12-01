# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.stock.models.stock_move_line import StockMoveLine as StockMoveLineBase
from odoo.addons.stock.models.stock_package_level import StockPackageLevel


class StockMoveLine(StockMoveLineBase):

    package_level_id = fields.Many2one[StockPackageLevel](index=True)
