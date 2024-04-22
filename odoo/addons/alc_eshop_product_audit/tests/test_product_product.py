# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase

from odoo.addons.extendable.tests.common import ExtendableMixin
from odoo.addons.shopinvader_product.schemas.product import ProductProduct


class TestProductSchema(TransactionCase, ExtendableMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.init_extendable_registry()
        cls.addClassCleanup(cls.reset_extendable_registry)

        cls.product = cls.env["product.product"].create(
            {"name": "test product", "tracking": "lot", "type": "product"}
        )
        if "is_web" in cls.env["product.category"]._fields:
            cls.category = cls.env.ref("alc_product_shop_category.master")
            cls.product.categ_ids = cls.category

    def test_00(self):
        product = ProductProduct.from_product_product(self.product)
        self.assertFalse(product.not_sold_on_website)
        self.product.sale_ok = False
        self.product.web_published = True
        product = ProductProduct.from_product_product(self.product)
        self.assertTrue(product.not_sold_on_website)
