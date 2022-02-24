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
        shop_parent = self.shopinvader_categ_obj.create(
            {
                "name": self.categ_parent.name,
                "lang_id": self.lang.id,
                "backend_id": self.backend.id,
                "record_id": self.categ_parent.id,
                "sequence": 10,
            }
        )
        self.assertEqual(shop_parent.url_key, "c/" + self.categ_parent.name.lower())
        shop_child = self.shopinvader_categ_obj.create(
            {
                "name": self.product_category.name,
                "lang_id": self.lang.id,
                "backend_id": self.backend.id,
                "record_id": self.product_category.id,
                "sequence": 20,
            }
        )
        self.assertEqual(
            shop_child.url_key,
            "c/"
            + self.categ_parent.name.lower()
            + "/"
            + self.product_category.name.lower(),
        )

    def test_product_url_prfx(self):
        self.assertTrue(self.shopinvader_variant.url_key.startswith("p/"))
