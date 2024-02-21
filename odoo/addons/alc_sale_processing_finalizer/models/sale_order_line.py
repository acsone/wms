# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api

from odoo.addons.sale_order_line_cancel.models import sale_order_line


class SaleOrderLine(sale_order_line.SaleOrderLine):
    @api.model
    def _get_moves_to_cancel(self):
        moves_to_cancel = super()._get_moves_to_cancel()
        # extend to move_orig_ids
        moves_to_cancel |= moves_to_cancel.mapped("move_orig_ids").filtered(
            lambda m: m.state not in ("done", "cancel")
        )
        return moves_to_cancel
