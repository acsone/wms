# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV (https://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.component.core import AbstractComponent


class BaseShopfloorService(AbstractComponent):
    """Base class for REST services"""

    _inherit = "base.shopfloor.service"

    def _log_call_in_db_values(self, _request, _id=None, params=None, **kw):
        values = super(BaseShopfloorService, self)._log_call_in_db_values(
            _request, _id, params=params, **kw
        )
        values["operator_id"] = self.shopfloor_user.id
        return values
