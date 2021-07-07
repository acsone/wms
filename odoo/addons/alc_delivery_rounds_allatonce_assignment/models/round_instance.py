# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class RoundInstance(models.Model):

    _inherit = "round.instance"

    def _confirm_picking_and_assign_moves(self, pickings, no_prepare=False):
        pickings_to_link = super(RoundInstance, self)._confirm_picking_and_assign_moves(
            pickings, no_prepare=no_prepare
        )

        # filter out pickings blocked by the picking_policy
        return pickings_to_link.filtered(lambda p: not p.is_blocked_by_picking_policy)
