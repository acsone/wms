# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class AlcWarehouseTest(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env.ref("stock.warehouse0")

    def test_warehouse_configuration(self):
        self.warehouse.reception_steps = "two_steps"
        self.warehouse.alc_constrains_configuration = True

        with self.assertRaises(UserError) as assert_warehouse:
            self.warehouse.reception_steps = "one_step"
        self.assertEqual(
            "You cannot modify the Warehouse configuration!",
            assert_warehouse.exception.name,
        )
