# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class RoundInstance(models.Model):

    _inherit = "round.instance"

    def _do_assign_pickings(self, pickings, no_prepare=False):
        pickings_by_partner = pickings.partition("partner_id")
        to_assign_ids = []
        for partner, partner_pickings in pickings_by_partner.items():
            if self._check_picking_assignable_to_round(partner_pickings, partner):
                to_assign_ids.extend(partner_pickings.ids)
        pickings_to_assign = self.env["stock.picking"].browse(to_assign_ids)
        return super(RoundInstance, self)._do_assign_pickings(
            pickings_to_assign, no_prepare=no_prepare
        )

    def _check_picking_assignable_to_round(self, pickings, partner):
        """
        return true if the all the prickings of the same partner are assignable
        to the delivery round
        """
        if partner in self.partner_ids:
            # we already have pickings for the same partner
            return True
        # first we filter out all the backorders
        pickings = pickings.filtered(lambda p: not p.backorder_id)
        # if we've at least one move that doens't require other lines -> we could
        # add all the pickings to the round
        for move in pickings.mapped("move_lines"):
            if not move.delivery_requires_other_lines:
                return True
        return False
