# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import pytz
from odoo import _, fields
from odoo.addons.component.core import AbstractComponent
from odoo.exceptions import AccessDenied

B2C_COLLECTION = "b2c.collection"


class BaseB2CService(AbstractComponent):
    _inherit = ["base.rest.service"]
    _name = "base.b2c.rest.service"
    _collection = B2C_COLLECTION

    @property
    def b2c_backend(self):
        """The b2c backend into a suspended security context"""
        return self.work.b2c_backend.suspend_security()

    @property
    def product_assortment_domain(self):
        return (
            self.b2c_backend.suspend_security().product_assortment_id._get_eval_domain()
        )

    def dispatch(self, method_name, _id=None, params=None):
        if self.env.user != self.env.ref("alc_b2c_connector.alc_b2c_rest_api_user"):
            raise AccessDenied(_("This user has no access to the B2C REST Api."))
        return super(BaseB2CService, self).dispatch(method_name, _id=_id, params=params)

    def _get_openapi_default_parameters(self):
        defaults = super(BaseB2CService, self)._get_openapi_default_parameters()
        defaults.append(
            {
                "name": "API-KEY",
                "in": "header",
                "description": "Auth API key",
                "required": True,
                "schema": {"type": "string"},
                "style": "simple",
            }
        )
        return defaults

    def _to_dt_utc_with_tz(self, value_str):
        if not value_str:
            return None
        dt = fields.Datetime.from_string(value_str)
        return pytz.utc.localize(dt, is_dst=False)
