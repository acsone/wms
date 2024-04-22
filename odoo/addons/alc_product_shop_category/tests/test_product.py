# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestProduct(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.cat_web = cls.env.ref("alc_product_shop_category.master")
        cls.model_cat = cls.env["product.category"]
        cls.product = cls.env["product.template"].create({"name": "Product"})

    def test_flow(self):
        vals_cat_1 = {"name": "1", "parent_id": self.cat_web.id}
        cat_1 = self.model_cat.create(vals_cat_1)
        self.assertTrue(cat_1.is_web)

        vals_cat_2 = {"name": "1", "parent_id": False}
        cat_2 = self.model_cat.create(vals_cat_2)
        self.assertFalse(cat_2.is_web)

        vals_cat_1_child = {"name": "1", "parent_id": cat_1.id}
        cat_1_child = self.model_cat.create(vals_cat_1_child)
        self.assertTrue(cat_1_child.is_web)

        cat_1.parent_id = False
        self.assertFalse(cat_1.is_web)
        self.assertFalse(cat_1_child.is_web)

        vals_cat_2_child = {"name": "1", "parent_id": cat_2.id}
        cat_2_child = self.model_cat.create(vals_cat_2_child)
        self.assertFalse(cat_2_child.is_web)

        cat_2.parent_id = self.cat_web
        self.assertTrue(cat_2.is_web)
        self.assertTrue(cat_2_child.is_web)

    def test_constrains(self):
        with self.assertRaisesRegex(ValidationError, "A web category is required"):
            self.product.web_published = True
        self.product.categ_ids = self.cat_web
        self.product.web_published = True
        with self.assertRaisesRegex(ValidationError, "A web category is required"):
            self.product.categ_ids = False
            self.product.web_published = True
