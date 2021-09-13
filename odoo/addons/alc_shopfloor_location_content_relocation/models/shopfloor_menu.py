# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, fields, models


class ShopfloorMenu(models.Model):

    _inherit = "shopfloor.menu"

    preserve_origin_location_kind_is_possible = fields.Boolean(
        compute="_compute_preserve_origin_location_kind_is_possible"
    )
    preserve_origin_location_kind = fields.Boolean(
        string="Preserve location kind",
        default=False,
        oldname="avoid_transfer_bin_to_reserve",
        help="If you tick this box, the transfer will target a location of same kind.",
    )

    @api.depends("scenario_id", "preserve_origin_location_kind")
    def _compute_preserve_origin_location_kind_is_possible(self):
        for menu in self:
            menu.preserve_origin_location_kind_is_possible = menu.scenario_id.has_option(
                "preserve_origin_location_kind"
            )

    @api.constrains(
        "scenario_id", "preserve_origin_location_kind",
    )
    def _check_preserve_origin_location_kind(self):
        for menu in self:
            if (
                menu.preserve_origin_location_kind
                and not menu.preserve_origin_location_kind_is_possible
            ):
                raise exceptions.ValidationError(
                    _(
                        u"Avoid transfer of bin to reserve is not allowed for menu {}."
                    ).format(menu.name)
                )
