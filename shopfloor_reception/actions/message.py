# Copyright 2025 ACSONE SA/NV (https://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from odoo import _

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class MessageAction(Component):
    _inherit = "shopfloor.message.action"

    def invalid_quantity(self, qty):
        return {
            "message_type": "error",
            "body": _(
                "Invalid quantity: '%(qty)s'.",
                qty=qty,
            ),
        }
