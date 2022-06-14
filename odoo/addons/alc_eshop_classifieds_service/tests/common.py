# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from contextlib import contextmanager

import mock
from dateutil.relativedelta import relativedelta

from odoo import fields

from odoo.addons.alc_eshop_classifieds.tests.common import TestClassifiedCase
from odoo.addons.base_rest.controllers.main import _PseudoCollection
from odoo.addons.component.core import WorkContext
from odoo.addons.component.tests.common import ComponentMixin


class TestClassifiedsService(TestClassifiedCase, ComponentMixin):
    @classmethod
    def setUpClass(cls):
        super(TestClassifiedsService, cls).setUpClass()
        cls.setUpComponent()
        cls.date_today = fields.Date.from_string(fields.Date.today())
        cls.date_tomorrow = cls.date_today + relativedelta(days=1)
        cls.date_yesterday = cls.date_today - relativedelta(days=1)
        cls.date_in_10_days = cls.date_today + relativedelta(days=10)

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

    def _get_classified_vals(self, **kwargs):
        vals = {
            "country_state_code": "WBR",
            "name": "fancy name",
            "body": "body",
            "category": "misc",
            "phone": "phone",
            "email": "email",
            "contact": "contact",
            "date_start": fields.Date.to_string(self.date_today),
            "date_end": fields.Date.to_string(self.date_in_10_days),
        }
        return dict(vals, **kwargs)
