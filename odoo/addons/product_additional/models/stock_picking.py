# -*- coding: utf-8 -*-
# Copyright 2017 Sylvain Van Hoof (Okia SPRL)
# Copyright 2017-2018 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def action_uncancel(self):
        """ Try to recover a canceled picking """
        additional_moves = self.mapped("pack_operation_ids.additional_move_id")
        moves_to_uncancel = self.mapped("move_lines") - additional_moves
        moves_to_uncancel.write({"state": "confirmed"})
        moves_to_uncancel.action_assign()

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
        result = super(StockPicking, self)._prepare_pack_ops(quants, forced_qties)
        if self.env.context.get("skip_additional"):
            return result

        if self.picking_type_subcode != "PICK":
            # This method is only intended for pickings
            return result

        product_obj = self.env["product.product"]

        # Group by picking/product
        packop_by_product = {}
        for pack_operation in result:
            if "product_id" not in pack_operation:
                continue

            picking_id = pack_operation["picking_id"]
            product_id = pack_operation["product_id"]
            key = (picking_id, product_id)
            if key not in packop_by_product:
                packop_by_product[key] = []
            packop_by_product[key].append(pack_operation)

        additional_moves = self.env["stock.move"]

        # Compute move to create
        # TODO: we should check if the move does not exist yet (as we must keep
        # it in some case where the main pack op is unlinked)
        for (picking_id, product_id), packops in packop_by_product.iteritems():
            product = product_obj.browse(product_id)
            if not product.additional_product_id:
                continue
            qty_main = 0.0
            for packop in packops:
                qty_main += packop["product_qty"]

            if not product.ratio_main_product:
                continue

            coefficient = int(qty_main / product.ratio_main_product)
            qty_add = coefficient * product.ratio_additional_product
            if not qty_add:
                continue
            additional_product = product.additional_product_id
            # Check the available qty
            qty_available = additional_product.immediately_usable_qty
            if not qty_available:
                continue
            qty_add = min(qty_add, qty_available)

            # Create moves into all the chained pickings of the main product
            # The moves must be created into the reverse order of the chain to
            # be able to link moves between us
            chained_moves = []
            picking = self.browse(picking_id)
            main_move = picking.move_lines.filtered(
                lambda a, product_id=product_id: a.product_id.id == product_id
            )
            move_dest = main_move and main_move[0]
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
                    "product_uom_qty": qty_add,
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
                }
                move_add = self.env["stock.move"].create(move_vals)
                move_dest_id = move_add.id
                _logger.debug(
                    "Created additional move %s (qty=%s) in the pickings %s",
                    move_add.id,
                    qty_add,
                    target_picking.id,
                )
                if move_dest == main_move:
                    for packop in packops:
                        packop["additional_move_id"] = move_add.id

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
