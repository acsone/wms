# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _

from odoo.addons.component.core import Component


class MessageAction(Component):
    _inherit = "shopfloor.message.action"

    def confirm_print_label(self):
        return {
            "message_type": "success",
            "body": _("The label for product will be printed."),
        }
