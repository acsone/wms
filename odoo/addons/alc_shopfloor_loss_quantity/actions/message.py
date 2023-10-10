# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _

from odoo.addons.shopfloor.actions.message import MessageAction as MessageActionBase


class MessageAction(MessageActionBase):
    def operation_loss_quantity_not_allowed(self):
        return {
            "message_type": "error",
            "body": _("You are not allowed to declare loss quantities"),
        }
