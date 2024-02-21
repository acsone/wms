# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero

from odoo.addons.sale_order_line_cancel.models import sale_order_line


class SaleOrderLine(sale_order_line.SaleOrderLine):
    def _check_moves_to_cancel(self, moves):
        if not moves:
            return
        if any(moves.picking_id.mapped("printed")):
            raise UserError(
                _("You cannot cancel a quantity that is part of a started picking")
            )
        done_preparation = moves.move_orig_ids.filtered(lambda m: m.state == "done")
        prepared_qty = sum(done_preparation.mapped("quantity_done"))
        dp = self.env["decimal.precision"].precision_get("Product Unit of Measure")

        if not float_is_zero(prepared_qty, precision_digits=dp) and not float_is_zero(
            prepared_qty - self.qty_delivered, precision_digits=dp
        ):
            raise UserError(
                _(
                    "The preparation is done for products: %(products)s",
                    products=", ".join(
                        done_preparation.product_id.mapped("display_name")
                    ),
                )
            )
        super()._check_moves_to_cancel(moves)
