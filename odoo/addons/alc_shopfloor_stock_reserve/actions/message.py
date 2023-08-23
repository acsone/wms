# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _

from odoo.addons.shopfloor.actions.message import MessageAction as MessageActionBase


class MessageAction(MessageActionBase):
    def no_reserve_location_found(self, location):
        return {
            "message_type": "error",
            "body": _(
                "No reserve location associated with location %s.", location.name
            ),
        }
