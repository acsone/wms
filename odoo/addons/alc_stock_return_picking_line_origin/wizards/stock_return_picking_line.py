# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.stock.wizard.stock_picking_return import ReturnPickingLine


class StockReturnPickingLine(ReturnPickingLine):

    origin = fields.Char(related="move_id.origin", readonly=True)
