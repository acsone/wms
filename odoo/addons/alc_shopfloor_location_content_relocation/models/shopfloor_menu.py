# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, fields, models


class ShopfloorMenu(models.Model):

    _inherit = "shopfloor.menu"

    avoid_transfer_bin_to_reserve_is_possible = fields.Boolean(
        compute="_compute_avoid_transfer_bin_to_reserve_is_possible"
    )
    avoid_transfer_bin_to_reserve = fields.Boolean(
        string="Avoid transfer of bin to reserve",
        default=False,
        help="If you tick this box, the transfer of a bin will not be put in reserve "
        "if some location items are already into a reserve",
    )

    @api.depends("scenario_id", "avoid_transfer_bin_to_reserve")
    def _compute_avoid_transfer_bin_to_reserve_is_possible(self):
        for menu in self:
            menu.avoid_transfer_bin_to_reserve_is_possible = menu.scenario_id.has_option(
                "avoid_transfer_bin_to_reserve"
            )

    @api.constrains(
        "scenario_id", "avoid_transfer_bin_to_reserve",
    )
    def _check_avoid_transfer_bin_to_reserve(self):
        for menu in self:
            if (
                menu.avoid_transfer_bin_to_reserve
                and not menu.avoid_transfer_bin_to_reserve_is_possible
            ):
                raise exceptions.ValidationError(
                    _(
                        u"Avoid transfer of bin to reserve is not allowed for menu {}."
                    ).format(menu.name)
                )
