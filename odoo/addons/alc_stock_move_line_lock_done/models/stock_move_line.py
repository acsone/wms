# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _
from odoo.exceptions import UserError

from odoo.addons.stock_move_line_lock_qty_done.models.stock_move_line import (
    StockMoveLine as StockMoveLineBase,
)


class StockMoveLine(StockMoveLineBase):
    def write(self, vals):
        has_group = self.env.user.has_group(
            "stock_move_line_lock_qty_done.group_stock_move_can_edit_done_qty"
        )
        fields_not_allowed_at_done_state = [
            "location_id",
            "location_dest_id",
            "lot_id",
            "package_id",
            "result_package_id",
            "owner_id",
            "product_uom_id",
            "reserved_uom_qty",
        ]
        update_not_allowed_at_done_state = any(
            k in fields_not_allowed_at_done_state for k in vals.keys()
        )
        for rec in self:
            if (
                rec.state == "done"
                and update_not_allowed_at_done_state
                and not has_group
            ):
                raise UserError(_("You are not allowed to edit done moves"))
        return super().write(vals)
