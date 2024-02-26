# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.addons.shopinvader_product.schemas import ProductCategory
from odoo.addons.shopinvader_search_engine.tests.common import TestCategoryBindingBase

from .common import TestURLLocalesCommon


class TestProductCategorySchema(TestCategoryBindingBase, TestURLLocalesCommon):
    _url_res_model = "product.category"

    @classmethod
    def _create_index(cls, lang):
        fr_index_values = cls._prepare_index_values(cls.backend)
        fr_index_values["lang_id"] = lang.id
        return cls.env["se.index"].create(fr_index_values)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.record = cls.category
        cls._setup_record_url()

    def test_0(self):
        category = self.env["product.category"].create({"name": "category"})
        category = ProductCategory.from_product_category(category)
        self.assertEqual(category.url_key_locales, {})

    def test_1(self):
        category = ProductCategory.from_product_category(self.category)
        self.assertEqual(
            category.url_key_locales, {"en_US": "url_key_en", "fr_FR": "url_key_fr"}
        )

    def test_2(self):
        """No lang set for the index."""
        self.se_categ_index.lang_id = False
        category = ProductCategory.from_product_category(self.category)
        self.assertEqual(category.url_key_locales, {"fr_FR": "url_key_fr"})
