# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields
from odoo.tests.common import TransactionCase


class TestStockMoveOrder(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.stock_move_obj = cls.env["stock.move"]
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product Test",
            }
        )

        cls.stock_move_obj.create(
            {
                "name": "Test Move A",
                "location_id": cls.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": cls.env.ref("stock.stock_location_stock").id,
                "product_uom_qty": 1.0,
                "product_id": cls.product.id,
                "product_uom": cls.product.uom_id.id,
                "date": "2022-12-30 10:00:00",
            }
        )

        cls.stock_move_obj.create(
            {
                "name": "Test Move B",
                "location_id": cls.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": cls.env.ref("stock.stock_location_stock").id,
                "product_uom_qty": 1.0,
                "product_id": cls.product.id,
                "product_uom": cls.product.uom_id.id,
                "date": "2022-12-31 10:00:00",
            }
        )

    def test_read_group(self):
        """Check that the date is in the result and its value is the oldest."""
        result = self.stock_move_obj.read_group(
            [
                (
                    "product_id",
                    "=",
                    self.product.id,
                )
            ],
            ["product_id", "date"],
            ["product_id"],
        )
        the_date = result[0].get("date")

        self.assertEqual(fields.Datetime.to_datetime("2022-12-30 10:00:00"), the_date)

    def test_no_read_group(self):
        try:
            with self.env.cr.savepoint():
                self.stock_move_obj._fields["date"].group_operator = None
                result = self.stock_move_obj.read_group(
                    [
                        (
                            "product_id",
                            "=",
                            self.product.id,
                        )
                    ],
                    ["product_id", "date"],
                    ["product_id"],
                )
                self.assertNotIn(
                    "date",
                    result[0].keys(),
                )
        finally:
            self.stock_move_obj._fields["date"].group_operator = "min"
