# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.stock.models.stock_move import StockMove as StockMoveBase
from odoo.addons.stock.models.stock_package_level import StockPackageLevel


class StockMove(StockMoveBase):

    package_level_id = fields.Many2one[StockPackageLevel](index=True)
