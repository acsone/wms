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
        cls.category = cls.env["product.category"].create({"name": "Test category"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "test product",
                "tracking": "lot",
                "type": "product",
                "categ_id": cls.category.id,
            }
        )
        cls.route_mto = cls.env.ref("stock.route_warehouse0_mto")
        cls.route_mto.active = True

    def test_00(self):
        product = ProductProduct.from_product_product(self.product)
        self.assertFalse(product.is_mto)
        self.assertEqual(product.route_from_categ_ids, [])
        self.product.route_ids += self.route_mto
        self.category.route_ids += self.route_mto
        self.category._compute_total_route_ids()
        product = ProductProduct.from_product_product(self.product)
        self.assertTrue(product.is_mto)
        self.assertEqual(product.route_from_categ_ids, ["Replenish on Order (MTO)"])
