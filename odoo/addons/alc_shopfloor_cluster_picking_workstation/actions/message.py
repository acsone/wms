# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _

from odoo.addons.component.core import Component


class MessageAction(Component):
    _inherit = "shopfloor.message.action"

    def workstation_set(self, ws):
        return {
            "message_type": "success",
            "body": _("Workstation set to {}").format(ws.name),
        }

    def workstation_not_found(self):
        return {
            "message_type": "error",
            "body": _("Workstation not found"),
        }
