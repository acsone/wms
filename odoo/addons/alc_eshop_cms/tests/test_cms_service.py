# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from contextlib import contextmanager

import mock

from odoo.tests.common import SavepointCase

from odoo.addons.base_rest.controllers.main import _PseudoCollection
from odoo.addons.component.core import WorkContext
from odoo.addons.component.tests.common import ComponentMixin

from .common import AlcEshopNewsMixin


class TestCmsService(SavepointCase, ComponentMixin, AlcEshopNewsMixin):
    @classmethod
    def setUpClass(cls):
        super(TestCmsService, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        super(TestCmsService, cls)._init_news()
        cls.setUpComponent()
        cls.partner = cls.env["res.partner"].create({"name": "partner"})

    # pylint: disable=method-required-super
    def setUp(self):
        # resolve an inheritance issue (common.SavepointCase does not call
        # super)
        SavepointCase.setUp(self)
        ComponentMixin.setUp(self)

    @classmethod
    @contextmanager
    def cms_service(cls):
        env = cls.env(context=dict(cls.env.context))
        collection = _PseudoCollection("shopinvader.backend", env)
        work = WorkContext(
            model_name="rest.service.registration",
            collection=collection,
            request=mock.Mock(),
        )
        yield work.component(usage="cms")

    def test_all_contents(self):
        with self.cms_service() as service:
            res = service.dispatch("content_search")
        self.assertTrue(res)
        self.assertIn(self.news_all_langs_json_fr, res["data"])
        self.assertIn(self.news_all_langs_json_en, res["data"])

    def test_get_content(self):
        lang, content_type, url = self.news_all_langs_json_fr["url"].split("/")
        with self.cms_service() as service:
            res = service.dispatch("content_get", lang, content_type, url)
        self.assertDictEqual(self.news_all_langs_json_fr, res)
