# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.alc_registration.tests.common import TestRegistrationMixin
from odoo.addons.fastapi.tests.common import FastAPITransactionCase

from ..routers import registrations_router


class TestRegistrationService(FastAPITransactionCase, TestRegistrationMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.default_fastapi_router = registrations_router

    def _get_registration_service_vals(self, **kwargs):
        vals = self._get_registration_vals()
        vals.pop("name")
        vals["firstname"] = "first"
        vals["lastname"] = "last"
        vals["title"] = "title_dr"
        vals["clientele"] = ["livestock", "pet"]
        vals.pop("occupation")
        vals["function"] = "function_nurse"
        return dict(vals, **kwargs)
