# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from contextlib import contextmanager

import mock

from odoo.addons.alc_registration.tests.common import TestRegistration
from odoo.addons.base_rest.controllers.main import _PseudoCollection
from odoo.addons.component.core import WorkContext
from odoo.addons.component.tests.common import ComponentMixin


class TestRegistrationService(TestRegistration, ComponentMixin):
    @classmethod
    def setUpClass(cls):
        super(TestRegistrationService, cls).setUpClass()
        cls.setUpComponent()

    @classmethod
    @contextmanager
    def registrations_service(cls):
        context = dict(cls.env.context)
        env = cls.env(context=context)
        collection = _PseudoCollection("shopinvader.backend", env)
        work = WorkContext(
            model_name="rest.service.registration",
            collection=collection,
            request=mock.Mock(),
        )
        yield work.component(usage="registrations")

    def _get_registration_service_vals(self, **kwargs):
        vals = self._get_registration_vals()
        vals.pop("name")
        vals["firstname"] = "first"
        vals["lastname"] = "last"
        vals["title"] = "title_dr"
        vals.pop("occupation")
        vals["function"] = "function_nurse"
        return dict(vals, **kwargs)
