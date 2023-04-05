# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import Command
from odoo.tests.common import TransactionCase


class TestStockLotUnarchive(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.lot_obj = cls.env["stock.lot"]
        cls.stock_move_obj = cls.env["stock.move"]
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product A",
                "type": "product",
                "tracking": "lot",
            }
        )
        cls.lot = cls.lot_obj.create(
            {
                "product_id": cls.product.id,
                "name": "TEST",
                "expiration_date": "2022-06-01",
                "company_id": cls.env.company.id,
            }
        )

        cls.newer_lot = cls.lot_obj.create(
            {
                "product_id": cls.product.id,
                "name": "TEST 2",
                "expiration_date": "2022-07-01",
                "company_id": cls.env.company.id,
            }
        )

    @classmethod
    def _archive(cls):
        cls.env["stock.lot.archive"]._archive_lots()

    def test_stock_lot_unarchive(self):
        self._archive()
        self.assertTrue(self.lot.is_archived)
        self.move = self.stock_move_obj.create(
            {
                "name": "Test",
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": self.env.ref("stock.stock_location_stock").id,
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
                "product_uom_qty": 1.0,
                "lot_ids": [Command.link(self.lot.id)],
            }
        )
        self.move._action_confirm()
        self.move._action_assign()
        # self.move.lot_ids = [Command.link(self.lot.id)]
        self.move.move_line_ids.write({"qty_done": 1.0, "lot_id": self.lot.id})

        self.move._action_done()
        self.assertFalse(self.lot.is_archived)
