# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo.tests import TransactionCase


class TestBestBeforeDate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.location_physical = cls.env.ref(
            "alc_stock_location_data.stock_location_vlb"
        )
        cls.location = cls.env["stock.location"].create(
            {
                "name": "Test physical",
                "usage": "internal",
                "location_id": cls.location_physical.id,
            }
        )
        cls.product_expirable = cls.env["product.product"].create(
            {
                "name": "Test expirable",
                "type": "product",
                "use_expiration_date": True,
                "tracking": "lot",
            }
        )
        cls.quant = cls.env["stock.quant"]
        cls.quant_base_value = {
            "product_id": cls.product_expirable.id,
            "location_id": cls.location.id,
            "quantity": 50,
            "available_quantity": 50,
        }
        cls.lot = cls.env["stock.lot"]
        cls.lot_base_values = {
            "name": "test_stock_lot_update 1",
            "product_id": cls.product_expirable.id,
            "company_id": cls.env.ref("base.main_company").id,
        }
        now = datetime.now()
        cls.date_not_old = now + relativedelta(days=30)
        cls.date_old = now + relativedelta(days=15)
        cls.date_oldest = now + relativedelta(days=7)

        vals = dict(cls.lot_base_values)
        vals.update({"name": "lot not old", "expiration_date": cls.date_not_old})
        cls.lot_not_old = cls.lot.create(vals)

    def test_best_before_date_base(self):
        self.quant._update_available_quantity(
            self.product_expirable, self.location, 10, lot_id=self.lot_not_old
        )
        self.product_expirable._compute_best_before_date()
        self.assertEqual(
            self.date_not_old.date(), self.product_expirable.best_before_date
        )

    def test_find_oldest_date(self):
        self.quant._update_available_quantity(
            self.product_expirable, self.location, 10, lot_id=self.lot_not_old
        )
        vals = dict(self.lot_base_values)
        vals.update({"name": "lot old", "expiration_date": self.date_old})
        lot_old = self.lot.create(vals)
        lot_old.flush_model()
        self.quant._update_available_quantity(
            self.product_expirable, self.location, 10, lot_id=lot_old
        )

        self.product_expirable._compute_best_before_date()
        self.assertEqual(self.date_old.date(), self.product_expirable.best_before_date)
