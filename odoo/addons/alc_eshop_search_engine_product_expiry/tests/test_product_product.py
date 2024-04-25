# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo.addons.shopinvader_product.schemas.product import ProductProduct
from odoo.addons.shopinvader_search_engine_product_stock.tests.common import (
    StockCommonCase,
)


class TestProductSchema(StockCommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context, queue_job__no_delay=True, index_id=cls.index.id
            )
        )
        cls.product = cls.env["product.product"].create(
            {"name": "test product", "tracking": "lot", "type": "product"}
        )
        cls.location_physical = cls.env.ref(
            "alc_stock_location_data.stock_location_vlb"
        )
        cls.location_physical.location_id = cls.warehouse_1.lot_stock_id
        cls.location = cls.env["stock.location"].create(
            {
                "name": "Test physical",
                "usage": "internal",
                "location_id": cls.location_physical.id,
            }
        )
        cls.binding = cls.product._add_to_index(cls.index)
        cls.product._compute_binding_ids()
        cls.env["ir.config_parameter"].set_param(
            "alc_stock_available_product_expiry.excludes_expired_lot_from_qty_available",
            True,
        )

    def _create_lot_at_date(self, date):
        lot = self.env["stock.lot"].create(
            {
                "name": date.isoformat(),
                "product_id": self.product.id,
                "expiration_date": date,
            }
        )
        self.env["stock.quant"].with_context(
            inventory_mode=True, queue_job__no_delay=True
        ).create(
            {
                "product_id": self.product.id,
                "inventory_quantity": 10,
                "location_id": self.location.id,
                "lot_id": lot.id,
            }
        ).action_apply_inventory()
        return lot

    def assertBestBeforeDate(self, date):
        product = ProductProduct.from_product_product(self.product)
        self.assertEqual(product.best_before_date, date.date())
        self.assertEqual(self.binding.state, "to_recompute")
        self.binding.recompute_json()
        self.assertEqual(self.binding.state, "to_export")
        self.assertEqual(
            self.binding.data.get("best_before_date"), date.date().isoformat()
        )

    def test_0(self):
        product = ProductProduct.from_product_product(self.product)
        self.assertEqual(product.best_before_date, None)

    def test_1(self):
        best_before_date = datetime.now() + relativedelta(days=30)
        self._create_lot_at_date(best_before_date)
        self.assertBestBeforeDate(best_before_date)
        self._create_lot_at_date(best_before_date - relativedelta(days=1))
        self.assertBestBeforeDate(best_before_date - relativedelta(days=1))

    def test_synchronize_with_same_best_before_date(self):
        self.binding.recompute_json()
        best_before_date = datetime.now() + relativedelta(days=30)
        self._create_lot_at_date(best_before_date)
        self.product.invalidate_recordset(["stock_data"])
        self.assertEqual(self.binding.state, "to_recompute")
        self.binding.recompute_json()
        self.assertDictEqual(self.binding.data.get("stock"), {"global": {"qty": 10}})
        self.assertEqual(self.binding.state, "to_export")
        # If we launch the synchronization again, the binding should not be
        # updated
        self.product.synchronize_all_binding_stock_level()
        self.assertEqual(self.binding.state, "to_export")

    def test_exclude_expired(self):
        best_before_date = datetime.now() - relativedelta(days=30)
        lot = self._create_lot_at_date(best_before_date)
        self.product.invalidate_recordset(["stock_data"])
        self.assertNotEqual(self.product.older_lot_id, lot)
        self.assertFalse(self.product.best_before_date)
        self.assertDictEqual(self.product.stock_data, {"global": {"qty": 0}})
