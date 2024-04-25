# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import datetime
from datetime import timedelta

from odoo.tests.common import TransactionCase


class TestStockAvailableProductExpiry(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product",
                "type": "product",
                "categ_id": cls.env.ref("product.product_category_all").id,
            }
        )
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.expired_lot = cls.env["stock.lot"].create(
            {
                "name": "Lot exipred",
                "product_id": cls.product.id,
                "expiration_date": "2024-01-01",
            }
        )
        cls.valid_lot = cls.env["stock.lot"].create(
            {
                "name": "Lot valid",
                "product_id": cls.product.id,
                "expiration_date": datetime.datetime.now() + timedelta(days=1),
            }
        )
        cls.location = cls.env["stock.location"].create(
            {
                "name": "Location",
                "usage": "internal",
                "location_id": cls.warehouse.lot_stock_id.id,
            }
        )
        cls.expired_quant = cls.env["stock.quant"].create(
            {
                "product_id": cls.product.id,
                "location_id": cls.location.id,
                "quantity": 5,
                "lot_id": cls.expired_lot.id,
            }
        )
        cls.valie_quant = cls.env["stock.quant"].create(
            {
                "product_id": cls.product.id,
                "location_id": cls.location.id,
                "quantity": 10,
                "lot_id": cls.valid_lot.id,
            }
        )

    def test_qty_available(self):
        self.assertEqual(self.product.qty_available, 15)
        self.env["ir.config_parameter"].set_param(
            "alc_stock_available_product_expiry.excludes_expired_lot_from_qty_available",
            True,
        )
        self.product.invalidate_recordset(["qty_available"])
        self.assertEqual(self.product.qty_available, 10)
        product_only_expired = self.product.with_context(compute_expired_only=True)
        product_only_expired.invalidate_recordset(["qty_available"])
        self.assertEqual(product_only_expired.qty_available, 5)
