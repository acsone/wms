# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.product.tests.common import ProductCommon


class TestAlcProductCategoryProperty(ProductCommon):
    @classmethod
    def _create_xml_id(cls, record, name):
        cls.env["ir.model.data"].create(
            {
                "name": name,
                "model": record._name,
                "res_id": record.id,
                "module": "alc_product_category_property",
            }
        )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._create_xml_id(cls.product_category, "product_category")
        cls.product_category_1 = cls.env["product.category"].create(
            {"name": "Test Category 1", "parent_id": cls.product_category.id}
        )
        cls._create_xml_id(cls.product_category_1, "product_category_1")
        cls.product_category_2 = cls.env["product.category"].create(
            {"name": "Test Category 2", "parent_id": cls.product_category_1.id}
        )
        cls._create_xml_id(cls.product_category_2, "product_category_2")
        cls.product_category_3 = cls.env["product.category"].create(
            {"name": "Test Category 3"}
        )
        cls._create_xml_id(cls.product_category_3, "product_category_3")

    def test_product_category_has_for_parent(self):
        self.assertFalse(self.product_category_3.has_for_parent(self.product_category))
        self.assertTrue(self.product_category_3.has_for_parent(self.product_category_3))
        self.assertTrue(self.product_category_2.has_for_parent(self.product_category))
        self.assertTrue(self.product_category_2.has_for_parent(self.product_category_1))
        self.assertTrue(self.product_category_1.has_for_parent(self.product_category))

    def test_product_category_has_for_parent_xml_id(self):
        self.assertEqual(
            self.product_category,
            self.env.ref("alc_product_category_property.product_category"),
        )
        self.assertEqual(
            self.product_category_1,
            self.env.ref("alc_product_category_property.product_category_1"),
        )
        self.assertEqual(
            self.product_category_2,
            self.env.ref("alc_product_category_property.product_category_2"),
        )
        self.assertEqual(
            self.product_category_3,
            self.env.ref("alc_product_category_property.product_category_3"),
        )
        self.assertFalse(
            self.product_category_3.has_for_parent_xml_id(
                "alc_product_category_property.product_category"
            )
        )
        self.assertTrue(
            self.product_category_3.has_for_parent_xml_id(
                "alc_product_category_property.product_category_3"
            )
        )
        self.assertTrue(
            self.product_category_2.has_for_parent_xml_id(
                "alc_product_category_property.product_category"
            )
        )
        self.assertTrue(
            self.product_category_2.has_for_parent_xml_id(
                "alc_product_category_property.product_category_1"
            )
        )
        self.assertTrue(
            self.product_category_1.has_for_parent_xml_id(
                "alc_product_category_property.product_category"
            )
        )
