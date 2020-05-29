# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import pytz
from odoo import _, fields
from odoo.addons.component.core import AbstractComponent
from odoo.exceptions import AccessDenied

CHRONOVET_COLLECTION = "chronovet.collection"


class BaseChronovetService(AbstractComponent):
    _inherit = ["base.rest.service"]
    _name = "base.chronovet.rest.service"
    _collection = CHRONOVET_COLLECTION

    @property
    def chronovet_backend(self):
        """The chronovet backend into a suspended security context"""
        return self.work.chronovet_backend.suspend_security()

    @property
    def product_assortment_domain(self):
        return (
            self.chronovet_backend.suspend_security().product_assortment_id._get_eval_domain()
        )

    def dispatch(self, method_name, _id=None, params=None):
        if self.env.user != self.env.ref(
            "alc_chronovet_connector.alc_chronovet_rest_api_user"
        ):
            raise AccessDenied(_("This user has no access to the Chronovet REST Api."))
        return super(BaseChronovetService, self).dispatch(
            method_name, _id=_id, params=params
        )

    def _get_openapi_default_parameters(self):
        defaults = super(BaseChronovetService, self)._get_openapi_default_parameters()
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
