# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import xmltodict

from odoo.addons.alc_eshop_api_cart.tests.common import TestEshopApiCartCase
from odoo.addons.alc_eshop_api_pickings.tests.common import TestPickingsServiceBase
from odoo.addons.alc_product_flattened_data.tests.common import TestProductFlattenedData

from .. import facade


class TestFacadeMixin:
    @classmethod
    def _init_data(cls):
        vals_partner = {"name": "P", "partner_type": "veterinary"}
        cls.partner = cls.env["res.partner"].create(vals_partner)

    def _get_service_facade(self, service):
        return facade.Facade.factory(self.env, self.partner, service)

    def assertXmlEqual(self, xml1, xml2):
        # xml1 and xml2 are strings
        # The comparison must ignore the order of elements and attributes
        self.assertEqual(
            xmltodict.parse(xml1, dict_constructor=dict),
            xmltodict.parse(xml2, dict_constructor=dict),
        )


class TestFacadeWithProductFlattenedData(TestProductFlattenedData, TestFacadeMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls._init_data()


class TestFacadePickings(TestPickingsServiceBase, TestFacadeMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        partner = cls.partner
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls._init_data()
        cls.partner = partner


class TestFacadeCart(TestEshopApiCartCase, TestFacadeMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls._init_data()
        cls.partner = cls.default_fastapi_authenticated_partner
        cls.product_1.default_code = "ABC"
