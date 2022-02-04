# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _

from odoo.addons.component.core import Component


class MessageAction(Component):
    _inherit = "shopfloor.message.action"

    def reserved_moves_in_current_location(self, location, product_names, picking):
        return {
            "message_type": "error",
            "body": _(
                u"Products {} are already reserved for picking {} in location {}. Please finish the picking(s) before starting a new one."
            ).format(
                (", ".join(product_names)),
                (", ".join(picking.mapped("name"))),
                location.name,
            ),
        }
