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
        cls.uom = cls.env.ref("uom.product_uom_meter")

    def test_00(self):
        self.product.dimensional_uom_id = self.uom
        product = ProductProduct.from_product_product(self.product)
        self.assertEqual(product.dimensional_uom_id.id, self.uom.id)
        self.assertEqual(product.dimensional_uom_id.name, self.uom.name)
