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
            if self._check_picking_assignable_to_round(partner, partner_pickings):
                to_assign_ids.extend(partner_pickings.ids)
                to_assign_ids.extend(
                    self._get_assignable_picking_ids(partner, partner_pickings)
                )
        pickings_to_assign = self.env["stock.picking"].browse(to_assign_ids)
        return super(RoundInstance, self)._do_assign_pickings(
            pickings_to_assign, no_prepare=no_prepare
        )

    def _check_picking_assignable_to_round(self, partner, pickings):
        """
        return true if all the pickings of the same partner are assignable
        to the delivery round
        """
        if partner in self.mapped("instance_customer_ids.partner_id"):
            # we already have pickings for the same partner
            return True
        if pickings.filtered("ignore_delivery_round_assign_block"):
            return True
        # if we've at least one move that doens't require other lines -> we could
        # add all the pickings to the round
        for move in pickings.mapped("move_lines").filtered(
            lambda m: m.state not in ("cancel", "done")
        ):
            if not move.delivery_requires_other_lines:
                return True
        return False

    def _get_assignable_picking_ids(self, partner, pickings):
        """Return all the pickings linked to the same shippings that are
        assignable.
        It's important to only takes pickings for the same shippings to
        ensure to not mix delivery carrier and therefore mix he delivery_rounds
        """
        shippings = pickings._get_all_dest_pickings().filtered(
            lambda r: r.picking_type_code == "outgoing"
            and r.state not in ("cancel", "done")
        )
        others_pickings = shippings._get_all_src_pickings() - pickings
        StockPicking = self.env["stock.picking"]
        domain = StockPicking._get_domain_picking_assignable_to_delivery_round(
            partners=partner
        )
        return others_pickings.filtered_domain(domain).ids
