# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.stock.models.stock_move import StockMove as BaseStockMove
from odoo.addons.stock.models.stock_rule import ProcurementGroup


class StockMove(BaseStockMove):

    group_id = fields.Many2one[ProcurementGroup](index=True)
