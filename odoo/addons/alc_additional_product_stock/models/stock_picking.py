# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.stock.models import stock_picking


class StockPicking(stock_picking.Picking):
    def _action_done(self):
        for rec in self:
            if (
                not rec.picking_type_id.no_backorder_for_additional_product
                or not rec._check_backorder()
            ):
                continue
            rec.move_ids._additional_move_split_and_cancel_not_done_qty()
        return super()._action_done()
