# -*- coding: utf-8 -*-
# Copyright 2021 Camptocamp SA (http://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _

from odoo.addons.component.core import Component


class ShopfloorWorkstation(Component):
    _inherit = "shopfloor.workstation"

    def setdefault(self, barcode):
        """Endpoint that receives a scanned barcode."""
        # redefine initial method since we use portal users available
        # as shopfloor_user
        ws = self.env["shopfloor.workstation"].search([("barcode", "=", barcode)])
        if ws:
            ws.set_as_default_on_user(self.shopfloor_user)
            message = {
                "message_type": "info",
                "body": _("Default workstation set to {}").format(ws.name),
            }
        else:
            message = {
                "message_type": "error",
                "body": _("Workstation not found"),
            }
        return self._response(
            message=message, data=self._convert_one_record(ws) if ws else {},
        )
