# -*- coding: utf-8 -*-
# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# Copyright 2018 Okia SPRL <sylvain@okia.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import _, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class StockPackOperation(models.Model):
    _inherit = "stock.pack.operation"

    def _skip_operation(self, pack_op_lot_id=None):
        """Unreserve the current move and recreate a new move with a different
        destination location. This method can be used if an operator
        wants to change the reserved moves (out of stock; scrap; ...)

        :param pack_op_lot_id: stock.pack.operation.lot
        """
        self.ensure_one()
        moves = self.linked_move_operation_ids.mapped("move_id")

        # Unreserve all operations
        moves.do_unreserve()

        # Get the available qty at that location
        # Consider only unreserved quants
        search_domain = [
            ("product_id", "=", self.product_id.id),
            ("location_id", "=", self.location_id.id),
            ("qty", ">", 0),
            ("reservation_id", "=", False),
        ]
        if pack_op_lot_id:
            search_domain.append(("lot_id", "=", pack_op_lot_id.lot_id.id))
        quants = self.env["stock.quant"].search(search_domain)
        if quants:
            # Block the quants that are available.
            # If the operation does not match a reserved move, no quant will be
            # returned.
            self.env.cr.execute(
                "SELECT id FROM stock_quant WHERE id in %s FOR UPDATE NOWAIT",
                (tuple(quants.ids),),
            )
            qty_available = sum([q.qty for q in quants])
            if pack_op_lot_id:
                qty_done = pack_op_lot_id.qty
            else:
                qty_done = self.qty_done
            qty_to_block = qty_available - qty_done
            if qty_to_block <= 0:
                raise UserError(_("No qty to block."))

            # Create a move to block this qty
            # Send to a temporary location part of the non-pickable stock
            # This will avoid that this lot will be use later.
            dest_location = self.env.ref("stock_lot_loss.stock_location_14019")

            move_line = {
                "name": "Skip Lot",
                "product_id": self.product_id.id,
                "product_uom_qty": qty_to_block,
                "picking_type_id": self.env.ref(
                    "stock_lot_loss.stock_picking_type_23"
                ).id,
                "location_id": self.location_id.id,
                "location_dest_id": dest_location.id,
                "product_uom": self.product_id.uom_id.id,
                "origin": u"Operator: %s" % self.env.user.name,
            }
            if pack_op_lot_id:
                move_line["restrict_lot_id"] = pack_op_lot_id.lot_id.id
            block_picking = self.env["stock.picking"].create(
                {
                    "picking_type_id": self.env.ref(
                        "stock_lot_loss.stock_picking_type_23"
                    ).id,
                    "location_id": self.location_id.id,
                    "location_dest_id": dest_location.id,
                    "move_lines": [(0, 0, move_line)],
                }
            )
            block_picking.action_confirm()
            block_picking.action_assign()

        # Recompute pack operations
        moves._recompute_pack_op()
