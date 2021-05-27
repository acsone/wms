# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV (https://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.component.core import Component


class ShopfloorUser(Component):
    _inherit = "shopfloor.user"

    def _user_info(self):
        return self.shopfloor_user.jsonify(self._user_info_parser, one=True)
