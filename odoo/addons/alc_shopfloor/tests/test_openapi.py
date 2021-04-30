# -*- coding: utf-8 -*-
# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# Copyright 2021 ACSONE SA/NV (https://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.shopfloor_base.tests.common_misc import OpenAPITestMixin

from .common import CommonCase


# pylint: disable=missing-return
class TestOpenAPICommonCase(CommonCase, OpenAPITestMixin):
    @classmethod
    def setUpClassVars(cls):
        super(TestOpenAPICommonCase, cls).setUpClassVars()
        # we don't really care about which menu and profile we use
        # to read the OpenAPI specs
        cls.menu = cls.env.ref("alc_shopfloor.shopfloor_menu_location_content_transfer")
        cls.profile = cls.env.ref("shopfloor_base.profile_demo_1")

    def test_openapi(self):
        self._test_openapi(menu=self.menu, profile=self.profile)
