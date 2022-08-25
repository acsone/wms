# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import models


class RoundInstance(models.Model):

    _inherit = "round.instance"

    def _confirm_picking_and_assign_moves(self, pickings, no_prepare=False):
        pickings_to_assign = self._check_pickings_can_be_assigned_to_delivery_rounds(
            pickings
        )
        return super(RoundInstance, self)._confirm_picking_and_assign_moves(
            pickings_to_assign, no_prepare
        )

    def _check_pickings_can_be_assigned_to_delivery_rounds(self, pickings):
        pickings_to_assign = self.env["stock.picking"]
        pickings_by_partner = defaultdict(lambda: self.env["stock.picking"])

        for picking in pickings:
            pickings_by_partner[picking.partner_id] |= picking

        for _, picks in pickings_by_partner.iteritems():
            has_only_backorders = self._check_backorders(picks)
            has_only_do_not_deliver_line = self._check_do_not_deliver_lines(picks)

            if not has_only_backorders and not has_only_do_not_deliver_line:
                pickings_to_assign |= picks

        return pickings_to_assign

    def _check_backorders(self, pickings):
        backorders = pickings.mapped("backorder_id")
        if len(backorders) == len(pickings):
            return True
        return False

    def _check_do_not_deliver_lines(self, pickings):
        if all(
            do_not_deliver
            for do_not_deliver in pickings.mapped("move_lines.do_not_deliver_line")
        ):
            return True
        return False
