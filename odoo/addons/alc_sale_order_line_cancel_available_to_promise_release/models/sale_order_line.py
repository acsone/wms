# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _
from odoo.exceptions import UserError

from odoo.addons.sale_order_line_cancel.models import sale_order_line


class SaleOrderLine(sale_order_line.SaleOrderLine):
    def _check_moves_to_cancel(self, moves):
        res = super()._check_moves_to_cancel(moves)
        for move in moves:
            iterator = move._get_chained_moves_iterator("move_orig_ids")
            next(iterator)  # skip the current move
            for pick_moves in iterator:
                printed_pickings = pick_moves.picking_id.filtered("printed")
                picking_names = ",".join(printed_pickings.mapped("name"))
                if printed_pickings:
                    raise UserError(
                        _(
                            "You cannot cancel a quantity that is part of a started picking (%(picking_names)s)",
                            picking_names=picking_names,
                        )
                    )
        return res
