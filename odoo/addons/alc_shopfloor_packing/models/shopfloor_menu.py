# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, fields, models


class ShopfloorMenu(models.Model):
    _inherit = "shopfloor.menu"

    pack_pickings_is_possible = fields.Boolean(
        compute="_compute_pack_pickings_is_possible"
    )
    pack_pickings = fields.Boolean(
        string="Pack pickings",
        default=False,
        help="If you tick this box, all the picked item will be put in pack"
        " before the transfer.",
    )

    @api.depends("scenario_id", "pack_pickings")
    def _compute_pack_pickings_is_possible(self):
        for menu in self:
            menu.pack_pickings_is_possible = menu.scenario_id.has_option(
                "pack_pickings"
            )

    @api.constrains("scenario_id", "pack_pickings")
    def _check_pack_pickings(self):
        for menu in self:
            if menu.pack_pickings and not menu.pack_pickings_is_possible:
                raise exceptions.ValidationError(
                    _(u"Pack pickings is not allowed for menu {}.").format(menu.name)
                )
