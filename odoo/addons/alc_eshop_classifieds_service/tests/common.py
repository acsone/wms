# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from contextlib import contextmanager

import mock

from odoo.addons.alc_eshop_classifieds.tests.common import TestClassifiedCase
from odoo.addons.base_rest.controllers.main import _PseudoCollection
from odoo.addons.component.core import WorkContext
from odoo.addons.component.tests.common import ComponentMixin


class TestClassifiedsService(TestClassifiedCase, ComponentMixin):
    @classmethod
    def setUpClass(cls):
        super(TestClassifiedsService, cls).setUpClass()
        cls.setUpComponent()

    @classmethod
    @contextmanager
    def classifieds_service(cls, partner=None):
        partner_id = (partner or cls.partner_1).id
        context = dict(cls.env.context, authenticated_partner_id=partner_id)
        env = cls.env(context=context)
        collection = _PseudoCollection("shopinvader.backend", env)
        work = WorkContext(
            model_name="rest.service.registration",
            collection=collection,
            request=mock.Mock(),
            authenticated_partner_id=partner_id,
        )
        yield work.component(usage="classified_ads")

    def publish(self, classifieds):
        classifieds.submit()
        classifieds.confirm()
