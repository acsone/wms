# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.stock.models import stock_package_level
from odoo.addons.stock.models.stock_picking import Picking


class StockPackageLevel(stock_package_level.StockPackageLevel):

    picking_id = fields.Many2one[Picking](index=True)
