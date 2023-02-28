# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime, timedelta

from odoo.tests.common import TransactionCase


class TestStockLot(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.today = datetime.today()
        cls.previous_week = cls.today - timedelta(days=7)
        cls.next_week = cls.today + timedelta(days=7)
        # enable lot
        cls.env.user.write(
            {"groups_id": [(4, cls.env.ref("stock.group_production_lot").id)]}
        )
        # product
        cls.prod1 = cls.env["product.product"].create(
            {"name": "Product 1", "type": "product", "use_expiration_date": True}
        )
        # Warehouse
        cls.warehouse_1 = cls.env["stock.warehouse"].create(
            {"name": "Warehouse1", "code": "WH1"}
        )
        # Locations
        cls.location_wh1_1 = cls.env["stock.location"].create(
            {
                "name": "TestLocation1",
                "location_id": cls.warehouse_1.view_location_id.id,
            }
        )
        # Lots
        StockLot = cls.env["stock.lot"]
        company_id = cls.env.ref("base.main_company").id
        cls.prod1_lot1 = StockLot.create(
            {
                "name": "Prod 1 Lot 1",
                "product_id": cls.prod1.id,
                "company_id": company_id,
                "removal_date": cls.next_week,
            }
        )
        cls.prod1_lot2 = StockLot.create(
            {
                "name": "Prod 1 Lot 2",
                "product_id": cls.prod1.id,
                "company_id": company_id,
                "removal_date": cls.next_week,
            }
        )
        # add some stock
        inventory_quant = cls.env["stock.quant"].create(
            {
                "location_id": cls.location_wh1_1.id,
                "product_id": cls.prod1.id,
                "lot_id": cls.prod1_lot1.id,
                "inventory_quantity": 50,
            }
        )
        inventory_quant.action_apply_inventory()
        inventory_quant = cls.env["stock.quant"].create(
            {
                "location_id": cls.location_wh1_1.id,
                "product_id": cls.prod1.id,
                "lot_id": cls.prod1_lot2.id,
                "inventory_quantity": 100,
            }
        )
        inventory_quant.action_apply_inventory()

    def test_1(self):
        """
        Data:

            A product in stock from 2 lots with removal_date in the future
        Test:
            check the lot_ids
        Expected Results:
            get 2 lots: lot1 and lot2 on product and product template
        """
        self.assertGreater(self.prod1_lot1.removal_date, self.today)
        self.assertGreater(self.prod1_lot2.removal_date, self.today)
        self.assertEqual(self.prod1.lot_ids, self.prod1_lot1 | self.prod1_lot2)
        self.assertEqual(
            self.prod1.product_tmpl_id.lot_ids, self.prod1_lot1 | self.prod1_lot2
        )

    def test_2(self):
        """
        Data:

            A product in stock from 2 lots with removal_date in the future
        Test:
            set the removal_date from lot2 in the past and check the lot_ids
        Expected Results:
            get 2 lots: lot1 and lot2 on product
            get 1 lot: lot1 on product template
        """
        self.assertGreater(self.prod1_lot1.removal_date, self.today)
        self.prod1_lot2.removal_date = self.previous_week
        self.assertGreater(self.today, self.prod1_lot2.removal_date)
        self.assertEqual(self.prod1.lot_ids, self.prod1_lot1 | self.prod1_lot2)
        self.assertEqual(self.prod1.product_tmpl_id.lot_ids, self.prod1_lot1)
