# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api

from odoo.addons.sale_order_line_cancel.wizards.sale_order_line_cancel import (
    SaleOrderLineCancel as OrderLineCancel,
)


class SaleOrderLineCancel(OrderLineCancel):
    @api.model
    def _get_moves_to_cancel(self, line):
        moves_to_cancel = super()._get_moves_to_cancel(line)
        # extend to move_orig_ids
        moves_to_cancel |= moves_to_cancel.mapped("move_orig_ids").filtered(
            lambda m: m.state not in ("done", "cancel")
        )
        return moves_to_cancel
