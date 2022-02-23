# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.shopinvader.tests import common


class TestAlcEShopModelsUrls(common.ProductCommonCase):
    @classmethod
    def setUpClass(cls):
        super(TestAlcEShopModelsUrls, cls).setUpClass()
        cls.shopinvader_categ_obj = cls.env["shopinvader.category"]
        cls.product_category = cls.env.ref("product.product_category_4")
        cls.categ_parent = cls.product_category.parent_id
        cls.lang = cls.env["res.lang"]._lang_get("en_US")

    def test_categ_url_prfx(self):
        shop_categ = self.shopinvader_categ_obj.create(
            {
                "name": self.product_category.name,
                "lang_id": self.lang.id,
                "backend_id": self.backend.id,
                "record_id": self.product_category.id,
            }
        )
        self.assertTrue(shop_categ.url_key.startswith("c/"))

    def test_product_url_prfx(self):
        self.assertTrue(self.shopinvader_variant.url_key.startswith("p/"))
