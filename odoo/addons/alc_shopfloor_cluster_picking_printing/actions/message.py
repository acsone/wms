# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _

from odoo.addons.component.core import Component


class MessageAction(Component):
    _inherit = "shopfloor.message.action"

    def no_product_label_printer_found(self):
        return {
            "message_type": "error",
            "body": _("No product label printer configured."),
        }

    def no_package_label_printer_found(self):
        return {
            "message_type": "error",
            "body": _("No package label printer configured."),
        }
