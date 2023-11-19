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

        cls.product = cls.env["product.product"].create({"name": "test product"})
        cls.storage_temperature = cls.env.ref(
            "alc_product_storage_temperature.product_storage_temperature_minus_12"
        )

    def test_00(self):
        product = ProductProduct.from_product_product(self.product)
        self.assertIsNone(product.storage_temperature_id)
        self.product.storage_temperature_id = self.storage_temperature
        product = ProductProduct.from_product_product(self.product)
        self.assertEqual(product.storage_temperature_id.id, self.storage_temperature.id)
        self.assertEqual(
            product.storage_temperature_id.name, self.storage_temperature.name
        )
