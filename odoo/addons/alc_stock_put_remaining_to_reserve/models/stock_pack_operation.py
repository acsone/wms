# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class StockPackOperation(models.Model):

    _inherit = "stock.pack.operation"

    is_action_put_in_reserve = fields.Boolean(
        compute="_compute_is_action_put_in_reserve", default=False
    )

    @api.depends("product_qty", "qty_done", "picking_id.picking_type_code")
    def _compute_is_action_put_in_reserve(self):
        # force prefetch
        self.mapped("picking_id.picking_type_id.code")
        for rec in self:
            rec.is_action_put_in_reserve = (
                (rec.qty_done - rec.product_qty <= 0)
                and rec.state not in ("done", "draft")
                and rec.picking_id.picking_type_code == "internal"
            )

    def _check_is_action_put_in_reserve(self):
        if any(not rec.is_action_put_in_reserve for rec in self):
            raise UserError(_("You are not allowed to put quantities in reserve"))

    def _put_remaining_quantities_in_reserve(self):
        self.ensure_one()
        dest_reserve_location = self.location_dest_id.get_location_reserve()
        if not dest_reserve_location:
            raise UserError(_("No reserve associated to this stock location."))

        moves = self.linked_move_operation_ids.mapped("move_id")
        # Unreserve all operations
        moves.do_unreserve()

        qty_remaining_to_reserve = self.product_qty - self.qty_done
        if qty_remaining_to_reserve <= 0:

            _logger.info(
                "No qty to move to reserve for product %s on picking %s",
                self.product_id.name,
                self.picking_id.name,
            )
            raise UserError(_("No qty to move to reserve."))

        picking_type_internal = self.env.ref("stock.picking_type_internal")

        move_line_vals = {
            "name": "Remaining quantities to reserve",
            "product_id": self.product_id.id,
            "product_uom_qty": qty_remaining_to_reserve,
            "picking_type_id": picking_type_internal.id,
            "location_id": self.location_id.id,
            "location_dest_id": dest_reserve_location.id,
            "product_uom": self.product_id.uom_id.id,
            "origin": u"Operator: %s" % self.env.user.name,
        }

        picking_to_reserve = self.env["stock.picking"].search(
            [
                ("picking_reserve_id", "=", self.picking_id.id),
                ("location_id", "=", self.location_id.id),
                ("location_dest_id", "=", dest_reserve_location.id),
            ]
        )
        if picking_to_reserve:
            move_line = self.env["stock.move"].create(move_line_vals)
            picking_to_reserve.write({"move_lines": [(4, move_line.id, _)]})
        else:
            picking_to_reserve = self.env["stock.picking"].create(
                {
                    "picking_type_id": picking_type_internal.id,
                    "picking_reserve_id": self.picking_id.id,
                    "location_id": self.location_id.id,
                    "location_dest_id": dest_reserve_location.id,
                    "move_lines": [(0, 0, move_line_vals)],
                }
            )
        picking_to_reserve.action_confirm()
        picking_to_reserve.action_assign()

        # Recompute pack operations
        moves._recompute_pack_op()
        return picking_to_reserve

    def action_put_in_reserve(self):
        self.ensure_one()
        self._check_is_action_put_in_reserve()
        picking = self._put_remaining_quantities_in_reserve()
        return picking
