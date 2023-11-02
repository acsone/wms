# Copyright 2023 ACSONE SA/NV
# License Other proprietary
from odoo.tests.common import TransactionCase


class TestIntrasttCategory(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.intrastat_code_1 = cls.env.ref(
            "account_intrastat.commodity_code_2018_1012100"
        )
        cls.intrastat_code_2 = cls.env.ref(
            "account_intrastat.commodity_code_2018_1012910"
        )
        cls.intrastat_code_3 = cls.env.ref(
            "account_intrastat.commodity_code_2018_1012990"
        )
        cls.category_A = cls.env["product.category"].create(
            {
                "name": "Category A",
                "parent_id": cls.env.ref("product.product_category_all").id,
            }
        )
        cls.category_A_B = cls.env["product.category"].create(
            {
                "name": "Category B",
                "parent_id": cls.category_A.id,
            }
        )

        cls.product = cls.env["product.product"].create(
            {
                "name": "Product Test A_B",
                "categ_id": cls.category_A_B.id,
            }
        )

    def test_intrastat_category(self):
        self.category_A.intrastat_code_id = self.intrastat_code_1
        self.assertEqual(self.intrastat_code_1, self.category_A_B.intrastat_code_id)
        self.category_A_B.specific_intrastat_code_id = self.intrastat_code_2
        self.assertEqual(self.intrastat_code_2, self.category_A_B.intrastat_code_id)

    def test_intrastat_product(self):
        self.category_A.intrastat_code_id = self.intrastat_code_1
        self.assertEqual(
            self.intrastat_code_1,
            self.product.intrastat_code_id,
        )
        self.category_A_B.intrastat_code_id = self.intrastat_code_2
        self.assertEqual(
            self.intrastat_code_2,
            self.product.intrastat_code_id,
        )
        self.product.specific_intrastat_code_id = self.intrastat_code_3
        self.assertEqual(
            self.intrastat_code_3,
            self.product.intrastat_code_id,
        )
