# -*- coding: utf-8 -*-
# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# Copyright 2018 Okia SPRL <sylvain@okia.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from collections import defaultdict, namedtuple

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


OperationGroupKey = namedtuple(
    "OperationGroupKey", ["location", "product", "package", "lot"]
)


class StockPackOperation(models.Model):
    _inherit = "stock.pack.operation"

    is_action_missing_qty_allowed = fields.Boolean(
        compute="_compute_is_action_missing_qty_allowed"
    )

    @api.depends("product_qty", "qty_done", "picking_id.picking_type_code")
    def _compute_is_action_missing_qty_allowed(self):
        # force prefetch
        self.mapped("picking_id.picking_type_id.code")
        for rec in self:
            rec.is_action_missing_qty_allowed = (
                (rec.qty_done - rec.product_qty <= 0)
                and rec.state not in ("done", "draft")
                and rec.picking_id.picking_type_code != "incoming"
            )

    def _check_is_action_missing_qty_allowed(self):
        if any(not rec.is_action_missing_qty_allowed for rec in self):
            raise UserError(_("You are not allowed to declare missing quantities"))

    def _is_done(self, lot=None):
        self.ensure_one()
        is_done = self.product_qty - self.qty_done <= 0
        if lot:
            pack_op_lot = self.pack_lot_ids.filtered(lambda l, lot=lot: l.lot_id == lot)
            is_done = pack_op_lot.qty_todo - pack_op_lot.qty <= 0
        return is_done

    def _group_operations(self, lot=None):
        """
        Return a list of operation by OperationGroupKey
        """
        ret = defaultdict(list)
        for rec in self:
            if lot and lot not in rec.pack_lot_ids.mapped("lot_id"):
                continue
            key = OperationGroupKey(
                location=rec.location_id,
                product=rec.product_id,
                package=rec.package_id,
                lot=lot,
            )
            ret[key].append(rec.id)

        return {k: self.browse(v) for k, v in ret.items()}

    # noqa: C901
    def _skip_operation(self, lot=None, raise_if_nothing_to_block=True):  # noqa: C901
        """Unreserve the current move and recreate a new move with a different
        destination location. This method can be used if an operator
        wants to change the reserved moves (out of stock; scrap; ...)

        :param lot: stock.production.lot
        """
        blocked_operations = []
        for group_key, operations in self._group_operations(lot=lot).items():
            operations_to_block = operations.filtered(
                lambda op, lot=lot: not op._is_done(lot=lot)
            )
            if operations_to_block != operations:
                not_blocked_product_descr = [
                    u"Picking: %s Product: %s"
                    % (op.picking_id.name, op.product_id.name)
                    for op in operations - operations_to_block
                ]
                if raise_if_nothing_to_block:
                    raise UserError(
                        _(u"No qty to block for: \n %s")
                        % "\n".join(not_blocked_product_descr)
                    )

                _logger.info(
                    u"No qty to block for: \n %s", "\n".join(not_blocked_product_descr)
                )
            if not operations_to_block:
                continue
            blocked_operations.extend(operations_to_block.ids)
            moves = operations_to_block.mapped(
                "linked_move_operation_ids.move_id"
            ).with_context(skip_additional=True)

            # Unreserve all operations
            moves.do_unreserve()

            # Get the available qty at that location
            # Consider only unreserved quants
            search_domain = [
                ("product_id", "=", group_key.product.id),
                ("location_id", "=", group_key.location.id),
                ("qty", ">", 0),
                ("reservation_id", "=", False),
            ]
            if lot:
                search_domain.append(("lot_id", "=", lot.id))
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
                if lot:

                    pack_op_lots = operations_to_block.mapped("pack_lot_ids").filtered(
                        lambda l, lot=lot: l.lot_id == lot
                    )
                    qty_done = sum(pack_op_lots.mapped("qty"))
                else:
                    qty_done = sum(operations_to_block.mapped("qty_done"))
                qty_to_block = qty_available - qty_done
                if qty_to_block <= 0:
                    if raise_if_nothing_to_block:
                        raise UserError(_("No qty to block."))
                    _logger.info(
                        "No qty to block for product %s", group_key.product.name
                    )
                    continue

                # Create a move to block this qty
                # Send to a temporary location part of the non-pickable stock
                # This will avoid that this lot will be use later.
                dest_location = self.env.ref("stock_lot_loss.stock_location_14019")

                move_line = {
                    "name": "Skip Lot",
                    "product_id": group_key.product.id,
                    "product_uom_qty": qty_to_block,
                    "picking_type_id": self.env.ref(
                        "stock_lot_loss.stock_picking_type_23"
                    ).id,
                    "location_id": group_key.location.id,
                    "location_dest_id": dest_location.id,
                    "product_uom": group_key.product.uom_id.id,
                    "origin": u"Operator: %s / Pickings: %s"
                    % (
                        self.env.user.name,
                        ", ".join(operations_to_block.mapped("picking_id.name")),
                    ),
                }
                if lot:
                    move_line["restrict_lot_id"] = lot.id
                block_picking = self.env["stock.picking"].create(
                    {
                        "picking_type_id": self.env.ref(
                            "stock_lot_loss.stock_picking_type_23"
                        ).id,
                        "location_id": group_key.location.id,
                        "location_dest_id": dest_location.id,
                        "move_lines": [(0, 0, move_line)],
                    }
                )
                block_picking.action_confirm()
                block_picking.action_assign()

        # Recompute pack operations
        # recompute pack op call action assign
        # keep the inital operation order
        ordered_operations = self.browse(
            [i for i in self.ids if i in blocked_operations]
        )
        moves = ordered_operations.mapped(
            "linked_move_operation_ids.move_id"
        ).with_context(skip_additional=True)
        moves._recompute_pack_op()

    def action_missing_qty(self):
        """This action process the operation and makes the remaining qty no more
        available into the stock at the same time of creating a picking to
        search for the qty loss. At the end, we try to recompute a new pack
        operation to find qty into an other place to complete the move.
        """
        self.ensure_one()
        self._check_is_action_missing_qty_allowed()
        if not self.pack_lot_ids:
            self._skip_operation()
            return True
        skipable_lots = self.pack_lot_ids.filtered(
            lambda pack_lot_id: pack_lot_id.qty < pack_lot_id.qty_todo
        )
        if len(skipable_lots) > 1:
            action_ctx = dict(self.env.context)
            action_ctx.update({"default_pack_operation_id": self.id})
            view_id = self.env.ref(
                "stock_lot_loss.stock_pack_operation_skip_lot_form_view"
            ).id
            return {
                "name": _("Select Lot/Serial Number to skip"),
                "type": "ir.actions.act_window",
                "view_type": "form",
                "view_mode": "form",
                "res_model": "stock.pack.operation.skip.lot",
                "views": [(view_id, "form")],
                "view_id": view_id,
                "target": "new",
                "context": action_ctx,
            }
        if len(skipable_lots) == 1:
            self._skip_operation(lot=skipable_lots.lot_id)
        return True
