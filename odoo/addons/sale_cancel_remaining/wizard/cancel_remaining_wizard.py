# -*- coding: utf-8 -*-
# Copyright 2018 Okia SPRL
# Copyright 2018 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import UserError


class CancelRemainingWizard(models.TransientModel):
    _name = "cancel.remaining.wizard"

    @api.model
    def cancel_remaining_qty(self):
        active_id = self._context.get("active_id")

        if not active_id:
            raise UserError(_("No sale order line ID found"))
        line = self.env["sale.order.line"].browse(active_id)

        internal_pickings = line.order_id.picking_ids.filtered(
            lambda picking: picking.picking_type_code == "internal"
            and picking.state not in ("cancel", "done")
        )
        if not internal_pickings:
            raise UserError(_("No picking can be canceled"))
        if True in internal_pickings.mapped("printed"):
            raise UserError(
                _("You cannot cancel a quantity that is part " "of a started picking")
            )

        cancel_moves = line.procurement_ids.mapped("move_ids").filtered(
            lambda m: m.state not in ("done", "cancel")
        )

        def _descend_moves(lvl):
            next_lvl = lvl.mapped("move_orig_ids")
            if next_lvl:
                lvl |= _descend_moves(next_lvl)
            return lvl

        if cancel_moves:
            cancel_moves = _descend_moves(cancel_moves)
            cancel_moves.with_context(cancel_procurement=True).action_cancel()
            # This will mark the procurement as done
            cancel_moves.mapped("procurement_id").check()

        line.write({"product_qty_canceled": line.product_qty_remains_to_deliver})
