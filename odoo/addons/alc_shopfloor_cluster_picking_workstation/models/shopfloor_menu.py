# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, fields, models


class ShopfloorMenu(models.Model):

    _inherit = "shopfloor.menu"
    scan_workstation = fields.Boolean(
        string="Scan workstation during scenario",
        default=False,
        help="If you tick this box, you will have to scan the workstation"
        " before starting the put in pack.",
    )
    scan_workstation_is_possible = fields.Boolean(
        compute="_compute_scan_workstation_is_possible"
    )

    @api.depends("scenario_id", "scan_workstation")
    def _compute_scan_workstation_is_possible(self):
        for menu in self:
            menu.scan_workstation_is_possible = menu.scenario_id.has_option(
                "scan_workstation"
            )

    @api.constrains("scenario_id", "scan_workstation")
    def _check_scan_workstation(self):
        for menu in self:
            if menu.scan_workstation and not menu.scan_workstation_is_possible:
                raise exceptions.ValidationError(
                    _(
                        u"Scanning workstation during process is not allowed for menu {}."
                    ).format(menu.name)
                )
