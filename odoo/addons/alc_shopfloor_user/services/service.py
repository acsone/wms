# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV (https://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.http import request

from odoo.addons.component.core import AbstractComponent


class BaseShopfloorService(AbstractComponent):
    """Base class for REST services"""

    _inherit = "base.shopfloor.service"

    @property
    def shopfloor_user(self):
        try:
            return (
                self.env["res.users"].browse(request.auth_api_key_id) or self.env.user
            )
        except RuntimeError:
            # in test mode request is unbound and raise RuntimeError
            return self.env.user
