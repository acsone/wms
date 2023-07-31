# Copyright 2021 ACSONE SA/NV (https://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.shopfloor_base.services.user import ShopfloorUser as ShopfloorUserBase


class ShopfloorUser(ShopfloorUserBase):
    def _user_info(self):
        return self.shopfloor_user.jsonify(self._user_info_parser, one=True)
