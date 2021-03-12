# -*- coding: utf-8 -*-
# Copyright 2016-2020 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2019-2020 Camptocamp
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import _, api, models

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.multi
    def _assign_picking_group_domain(self):
        self.ensure_one()
        domain = [
            ("customer_id", "=", self.group_id.customer_id.id),
            ("partner_id", "=", self.group_id.partner_id.id),
            ("location_id", "=", self.location_id.id),
            ("location_dest_id", "=", self.location_dest_id.id),
            ("picking_type_id", "=", self.picking_type_id.id),
            ("printed", "=", False),
            ("state", "not in", ("draft", "cancel", "done")),
        ]
        return domain

    def _get_new_picking_values(self):
        """ Prepares a new picking for this move as it could not be assigned to
        another picking.
        Add the customer from the procurement group.
        """
        self.ensure_one()
        res = super(StockMove, self)._get_new_picking_values()
        res["customer_id"] = self.group_id.customer_id.id
        return res

    @api.multi  # noqa: C901
    def assign_picking(self):
        """Try to assign the moves to an existing picking
        that has not been reserved yet and that does not have the same
        procurement group but the same partner, locations and picking type
        (moves should already have them identical). Otherwise, create a new
        picking to Assign them to.
        """
        moves_to_group = self.filtered(lambda x: x.picking_type_id.groupbypartner)

        moves_to_not_group = self - moves_to_group
        if moves_to_not_group:
            super(StockMove, moves_to_not_group).assign_picking()

        pick_obj = self.env["stock.picking"]
        pickings_cache = {}
        recompute_sale_pickings = bool(moves_to_group.mapped("picking_id"))
        for move in moves_to_group:
            domain = move._assign_picking_group_domain()
            if str(domain) in pickings_cache:
                pickings = pickings_cache[str(domain)]
            else:
                pickings = pick_obj.search(domain, order="weight")
                pickings_cache[str(domain)] = pickings

            max_weight = (
                move.picking_type_id.groupbypartner_maxweight
                - move.product_id.weight * move.product_qty
            )
            backorder_orig_id = move.picking_id

            # Preferably assign the move in a picking having a move with the
            # same group_id. Necessary for pushed moves
            if len(pickings) > 1:

                # pylint: disable=cell-var-from-loop
                def key(r):
                    return not (
                        move.group_id
                        and move.group_id
                        in r.move_lines.filtered(
                            lambda m: m.state not in ("cancel", "done")
                        ).mapped("group_id")
                    )

                pickings = pickings.sorted(key=key)
            # Select the right picking to assign to
            for picking in pickings:
                # Ensure the move related carrier matches the picking related
                # carrier. This is not part of _assign_picking_group_domain for
                # performance reasons
                if picking.group_id.carrier_id != move.group_id.carrier_id:
                    continue
                if (
                    move.picking_id != picking
                    and move.picking_type_id.groupbypartner_maxweight
                    and picking.weight > max_weight
                ):
                    continue
                if move.picking_id != picking:
                    # assign move to picking
                    _logger.debug(
                        "Assign move %s to existing picking %s (%s)",
                        move.id,
                        picking.id,
                        picking.name,
                    )
                    picking._lock()
                    move.picking_id = picking.id
                    if backorder_orig_id:
                        backorder_orig_id.message_post(
                            body=_(
                                "Remaining move '%s' of qty %s and origin '%s' "
                                "moved to exiting picking "
                                "<em>%s</em> used as "
                                "a backorder."
                            )
                            % (
                                move.product_id.display_name,
                                move.product_uom_qty,
                                move.group_id.name,
                                picking.name,
                            )
                        )
                # unreserve moves having an operation for that product
                # Note: (re)check availability (action_assign) does not
                # work on added move where an operation already exists for
                # that product. To not recompute all the quants of the
                # picking, we delete only the pack operation to recompute.
                # No need to perform the assignment now (new pack operation
                # creation), it is performed later when the procurement is
                # run.
                # If the new move is in waiting state (line added in a
                # ship), then do not cleanup the pack operation as it won't
                # be recomputed
                if move.state == "waiting":
                    break
                operations_to_recompute = picking.pack_operation_ids.filtered(
                    lambda op, m=move: op.product_id == m.product_id
                )
                if operations_to_recompute:
                    _logger.debug("Cleaning operations %s", operations_to_recompute.ids)
                    op_linked_moves = operations_to_recompute.mapped(
                        "linked_move_operation_ids.move_id"
                    )
                    operations_to_recompute.unlink()
                    op_linked_moves.do_unreserve()
                else:
                    move.do_unreserve()
                break

            else:
                if self.env.context.get("no_new_picking") and not any(
                    pm.state == "done" for pm in move.picking_id.move_lines
                ):
                    # if picking has not been processed, we can use it as backorder
                    move.picking_id._lock()
                    picking = move.picking_id
                else:
                    # create a new picking
                    values = move._get_new_picking_values()
                    picking = pick_obj.create(values)
                    _logger.debug(
                        "Assign move %s to new picking %s (%s)",
                        move.id,
                        picking.id,
                        picking.name,
                    )
                    if backorder_orig_id:
                        picking.message_post(
                            body=_("Backorder of %s") % backorder_orig_id.name
                        )
                        backorder_orig_id.message_post(
                            body=_(
                                "Remaining move '%s' moved to new backorder "
                                "<em>%s</em>."
                            )
                            % (move.product_id.display_name, picking.name)
                        )
                    move.picking_id = picking.id
                if str(domain) not in pickings_cache:
                    pickings_cache[str(domain)] = picking
                else:
                    pickings_cache[str(domain)] |= picking
                move.do_unreserve()
                # see standard assign_picking for why recompute is called
                move.recompute()
        if recompute_sale_pickings:
            procurement_groups = moves_to_group.mapped("group_id")
            sales = self.env["sale.order"].search(
                [("procurement_group_id", "in", procurement_groups.ids)]
            )
            # force recompute of picking_ids
            sales.modified(["procurement_group_id"])
        return True

    @api.multi
    def action_cancel(self):
        """ Prevent to cancel a move from a printed picking and recompute pack
        operations """
        _logger.debug("Canceling moves %s", self.ids)
        res = super(StockMove, self).action_cancel()
        if not self.env.context.get("no_recompute_pack"):
            pickings = self.mapped("picking_id").filtered(
                lambda picking: picking.state != "cancel"
            )
            products = self.mapped("product_id")
            moves = pickings.mapped("move_lines").filtered(
                lambda move: move.state == "confirmed" and move.product_id in products
            )
            if moves:
                # action_assign requires to clean existing pack operation
                moves.mapped("linked_move_operation_ids.operation_id").unlink()
                _logger.debug("Re-check availability for moves %s", moves.ids)
                moves.action_assign(no_prepare=True)
            # recompute pack op
            _logger.debug("Recompute pack operations")
            pickings.do_prepare_partial()
            # Recompute the weight for each picking
            self.exists().mapped("picking_id")._cal_weight()
        return res
