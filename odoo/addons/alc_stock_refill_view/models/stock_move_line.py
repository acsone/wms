# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.stock.models import stock_move_line, stock_picking


class StockMoveLine(stock_move_line.StockMoveLine):
    # By default odoo makes the field compute and searchable to support
    # the case where the move line is related to a manufactory order and the
    # one where the move line is related to a picking. We don't need this
    # but need to store the field to allow to group by it.
    picking_type_id = fields.Many2one[stock_picking.PickingType](
        related="picking_id.picking_type_id",
        store=True,
        readonly=True,
        index=True,
    )
