# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase

from odoo.addons.extendable.tests.common import ExtendableMixin

from ..schemas import ProductProduct


class TestProductExpiryInSchema(TransactionCase, ExtendableMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.init_extendable_registry()
        cls.addClassCleanup(cls.reset_extendable_registry)

        cls.product = cls.env["product.product"].create({"name": "test product"})

    def test_00(self):
        product = ProductProduct.from_product_product(self.product)
        self.assertEqual(product.specials, [])
        self.env["product.discount.special"].create(
            {
                "sequence": 1,
                "date_start": "2022-10-01",
                "date_end": "2022-12-01",
                "product_template_id": self.product.product_tmpl_id.id,
            }
        )
        product = ProductProduct.from_product_product(self.product)
        self.assertEqual(len(product.specials), 1)
        discount = product.specials[0]
        self.assertEqual(discount.sequence, 1)
        self.assertEqual(discount.date_start, "2022-10-01")
        self.assertEqual(discount.date_end, "2022-12-01")
        self.env["product.discount.special"].create(
            {
                "sequence": 2,
                "date_start": "2022-01-01",
                "date_end": "2022-02-01",
                "product_template_id": self.product.product_tmpl_id.id,
            }
        )
        product = ProductProduct.from_product_product(self.product)
        self.assertEqual(len(product.specials), 2)
