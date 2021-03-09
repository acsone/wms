# -*- coding: utf-8 -*-
# Copyright 2017 Sylvain Van Hoof (Okia SPRL)
# Copyright 2017-2018 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from collections import defaultdict

from odoo import api, models

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _get_moves_by_main_product(self):
        """ Return a list of moves of products defined with an additional_product_id
        """
        moves_by_main_product = defaultdict(list)
        for move in self.mapped("move_lines").filtered(lambda m: m.state == "assigned"):
            product = move.product_id
            if product.additional_product_id and product.ratio_main_product:
                moves_by_main_product[product].append(move.id)
                continue
        return {
            p: self.env["stock.move"].browse(ids)
            for p, ids in moves_by_main_product.items()
        }

    def _get_packops_by_product_id(self, pack_ops):
        # Group by picking/product
        packops_qty_by_product = defaultdict(list)
        for pack_operation in pack_ops:
            if "product_id" not in pack_operation:
                continue

            picking_id = pack_operation["picking_id"]
            product_id = pack_operation["product_id"]
            key = (picking_id, product_id)
            packops_qty_by_product[key].append(pack_operation)
        return packops_qty_by_product

    def _purge_additional_moves(self):
        moves_to_cancel = (
            self.mapped("move_lines")
            .filtered("is_additional_move")
            .with_context(no_recompute_pack=True, force_cancel=True)
        )
        move_ids_to_unlink = []
        if moves_to_cancel:
            _logger.debug("Canceling additional moves %s", moves_to_cancel.ids)
            additional_moves_dest = moves_to_cancel.mapped("move_dest_id")
            while additional_moves_dest:
                additional_moves_dest.action_cancel()
                move_ids_to_unlink.extend(additional_moves_dest.ids)
                additional_moves_dest = additional_moves_dest.mapped("move_dest_id")
            moves_to_cancel.action_cancel()
            move_ids_to_unlink.extend(moves_to_cancel.ids)

        moves_to_unlink = (
            self.env["stock.move"]
            .sudo()
            .browse(move_ids_to_unlink)
            .with_context(no_recompute_pack=True, force_cancel=True)
        )
        # * We need to unlink that canceled move otherwise do_unreserve
        #   will complain for 'Cannot unreserve a done move'
        # * Calling sudo as a standard picker cannot delete a stock.move
        # * Reception orders are failing on this unlink
        if "RECEIVE" not in moves_to_unlink.mapped("picking_id.picking_type_subcode"):
            moves_to_unlink.unlink()

    @api.multi  # noqa: C901
    def _prepare_pack_ops(self, quants, forced_qties):
        """
        This method will add additional products on stock
        moves and pack operations.
        There are three main steps:
        1. Call super and retrieve the result
        2. Sum quantities by picking and product
        3. Create additional moves
        4. Valid (action_confirm) and assign moves (action_assign)
        5. Append additional pack operations values to result
        :param quants:
        :param forced_qties:
        :return:
        """
        self.ensure_one()
        if self.picking_type_subcode == "PICK" and not self.env.context.get(
            "skip_additional"
        ):
            # remove additional moves since they will be recreated there after
            self._purge_additional_moves()
        result = super(StockPicking, self)._prepare_pack_ops(quants, forced_qties)
        if self.env.context.get("skip_additional"):
            return result

        if self.picking_type_subcode != "PICK":
            # This method is only intended for pickings
            return result

        additional_moves = self.env["stock.move"]

        packops_by_product = self._get_packops_by_product_id(result)

        for product, main_moves in self._get_moves_by_main_product().items():
            packops = packops_by_product.get((self.id, product.id), [])
            qty_main = sum(p["product_qty"] for p in packops)
            if not qty_main:
                continue
            # 1 compute qty to add
            coefficient = int(qty_main / product.ratio_main_product)
            qty_add = coefficient * product.ratio_additional_product
            if not qty_add:
                continue
            # remove qty already assigned by existing additional moves
            additional_product = product.additional_product_id

            # Check the available qty
            qty_available = additional_product.immediately_usable_qty
            if not qty_available:
                continue
            qty_add = min(qty_add, qty_available)

            # create additional moves by main move proportionally to the qty
            # into the main move and according to the qty to add.
            # In this way we ensure that we create an additional move by main
            # move linked to the same procurement
            for main_move in main_moves:
                additional_qty = (
                    product.ratio_additional_product * main_move.product_qty
                )
                additional_qty = min(additional_qty, qty_add)
                if not additional_qty:
                    break
                # compute the remaining qty to add
                qty_add = qty_add - additional_qty

                # Create moves into all the chained pickings of the main product
                # The moves must be created into the reverse order of the chain to
                # be able to link moves between us
                chained_moves = []
                move_dest = main_move
                while move_dest:
                    chained_moves.append(move_dest)
                    move_dest = move_dest.move_dest_id
                move_dest_id = False
                chained_moves.reverse()
                for move_dest in chained_moves:
                    target_picking = move_dest.picking_id
                    move_vals = {
                        "name": u"ADDITIONAL PRODUCT: %s (FROM %s)"
                        % (additional_product.display_name, product.display_name),
                        "sequence": 9999,
                        "product_id": additional_product.id,
                        "product_uom_qty": additional_qty,
                        "product_uom": additional_product.uom_id.id,
                        "partner_id": target_picking.partner_id.id,
                        "location_id": target_picking.location_id.id,
                        "location_dest_id": target_picking.location_dest_id.id,
                        "picking_id": target_picking.id,
                        "picking_type_id": target_picking.picking_type_id.id,
                        "origin": target_picking.name,
                        "group_id": target_picking.group_id.id,
                        "is_additional_move": True,
                        "rule_id": move_dest.rule_id.id,
                        "propagate": move_dest.propagate,
                        "move_dest_id": move_dest_id,
                        "procurement_id": move_dest.procurement_id.id,
                        "warehouse_id": move_dest.warehouse_id.id,
                        "main_move_id": move_dest.id,
                    }
                    move_add = self.env["stock.move"].create(move_vals)
                    move_dest_id = move_add.id
                    _logger.debug(
                        "Created additional move %s (qty=%s) in the pickings %s",
                        move_add.id,
                        qty_add,
                        target_picking.id,
                    )
                    additional_moves |= move_add

        # Assign moves
        if additional_moves:
            additional_moves.action_confirm()
            additional_moves.action_assign(no_prepare=True)
            additional_quants = additional_moves.mapped("reserved_quant_ids")
            additional_result = super(StockPicking, self)._prepare_pack_ops(
                additional_quants, {}
            )
            result += additional_result

        return result
