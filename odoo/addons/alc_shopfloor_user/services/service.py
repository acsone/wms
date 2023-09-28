# Copyright 2021 ACSONE SA/NV (https://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.http import request

from odoo.addons.component.core import AbstractComponent


class BaseShopfloorService(AbstractComponent):
    """Base class for REST services."""

    _inherit = "base.shopfloor.service"

    @property
    def shopfloor_user(self):
        try:
            auth_api_key_id = (
                self.env["auth.api.key"].sudo().browse(request.auth_api_key_id)
            )
            return (
                self.env["res.users"].browse(auth_api_key_id.shopfloor_user_id.id)
                or self.env.user
            )
        except RuntimeError:
            # in test mode request is unbound and raise RuntimeError
            return self.env.user

    def dispatch(self, method_name, *args, params=None):
        if self.shopfloor_user and self.shopfloor_user != self.env.user:
            # If shopfloor user is set we call the method in his name with sudo mode
            self.env.uid = self.shopfloor_user.id
            self.env.user = self.shopfloor_user
            self.env.su = True
        return super().dispatch(method_name, *args, params=params)
