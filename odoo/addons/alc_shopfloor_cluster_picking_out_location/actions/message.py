# Copyright 2022 Camptocamp SA (http://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _

from odoo.addons.component.core import Component


class MessageAction(Component):
    _inherit = "shopfloor.message.action"

    def out_trolley_blocked_by_delivery(self):
        return {
            "message_type": "error",
            "body": _(
                "This trolley is already blocked by another release channel, select a new one."
            ),
        }

    def package_already_scanned(self):
        return {
            "message_type": "error",
            "body": _("Package already scanned. Please scan another one."),
        }

    def package_not_in_batch(self):
        return {
            "message_type": "error",
            "body": _(
                "Package not in the picking batch. Please scan a correct package."
            ),
        }

    def package_does_not_exist(self):
        return {
            "message_type": "error",
            "body": _("Package does not exist. Please scan a correct package."),
        }
