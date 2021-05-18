# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class SalesService(Component):

    _inherit = "sales.service"

    def _validator_create(self):
        res = super(SalesService, self)._validator_create()
        res["carrier"] = {
            "type": "string",
            "nullable": True,
            "required": False,
            "allowed": ["GLS_BE", "GLS_FR"],
        }
        return res
