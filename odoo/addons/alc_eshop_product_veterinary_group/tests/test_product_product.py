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
        cls.veterinary_group = cls.env["veterinary.group"].create(
            {"name": "veterinary group"}
        )

    def test_00(self):
        product = ProductProduct.from_product_product(self.product)
        self.assertEqual(product.veterinary_groups, [])
        self.product.veterinary_group_ids = self.veterinary_group
        product = ProductProduct.from_product_product(self.product)
        self.assertEqual(len(product.veterinary_groups), 1)
        veterinary_group = product.veterinary_groups[0]
        self.assertEqual(veterinary_group.id, self.veterinary_group.id)
        self.assertEqual(veterinary_group.name, self.veterinary_group.name)
