# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _

from odoo.addons.component.core import Component


class MessageAction(Component):
    _inherit = "shopfloor.message.action"

    def all_waiting_availability(self):
        return {
            "message_type": "success",
            "body": _("All the products are out of stock, start a new batch."),
        }
