# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader.tests.common import ProductCommonCase


class ProductCase(ProductCommonCase):
    def setUp(self):
        super(ProductCase, self).setUp()
        self.cat_web_root = self.env.ref("alc_product_shop_category.master")
        vals_cat_web_child = {"name": "1", "parent_id": self.cat_web_root.id}
        self.cat_web_child = self.env["product.category"].create(vals_cat_web_child)

    def test_filter_categories(self):
        # Note that web_root is not a web category by itself.
        # given
        self.template.categ_ids = self.cat_web_child
        # when
        exported_categories = self.template.shopinvader_bind_ids._get_categories()
        # then: other categories have been filtered out
        self.assertEqual(exported_categories, self.cat_web_child)
