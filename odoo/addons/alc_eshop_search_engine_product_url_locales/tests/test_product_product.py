# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.addons.shopinvader_product.schemas import ProductProduct
from odoo.addons.shopinvader_search_engine.tests.common import TestProductBindingBase

from .common import TestURLLocalesCommon


class TestProductSchema(TestProductBindingBase, TestURLLocalesCommon):
    _url_res_model = "product.template"

    @classmethod
    def _create_index(cls, lang):
        index_values = cls._prepare_index_values(cls, cls.backend)
        index_values["lang_id"] = lang.id
        return cls.env["se.index"].create(index_values)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.record = cls.product
        cls._setup_record_url()

    def test_0(self):
        product = self.env["product.product"].create({"name": "product"})
        product = ProductProduct.from_product_product(product)
        self.assertEqual(product.url_key_locales, {})

    def test_1(self):
        product = ProductProduct.from_product_product(self.product)
        self.assertEqual(
            product.url_key_locales, {"en_US": "url_key_en", "fr_FR": "url_key_fr"}
        )
