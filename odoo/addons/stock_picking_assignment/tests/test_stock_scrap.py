# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import SavepointCase


class TestStockScrap(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestStockScrap, cls).setUpClass()
        cls.demo_user = cls.env.ref("base.user_demo")
        cls.StockScrap = cls.env["stock.scrap"]
        cls.stock_loc = cls.env.ref("stock.stock_location_stock")

        # Stockable product
        cls.product_stockable = cls.env["product.product"].create(
            {
                "type": "product",
                "name": "Stockable Product",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "uom_po_id": cls.env.ref("product.product_uom_unit").id,
            }
        )

        cls._update_product_qty(cls.product_stockable)

    @classmethod
    def _update_product_qty(cls, product):
        product_qty = cls.env["stock.change.product.qty"].create(
            {
                "location_id": cls.stock_loc.id,
                "product_id": product.id,
                "new_quantity": 100.0,
            }
        )
        product_qty.change_product_qty()
        return product_qty

    def _get_scrap_values(self):
        return {
            "name": "test inventor",
            "product_id": self.product_stockable.id,
            "product_uom_id": self.ref("product.product_uom_unit"),
        }

    def test_00(self):
        """
        Data:
            Nope
        Test case:
            Create a scrap without operator
        Expected result:
            The operator must be set to the current user
        """
        vals = self._get_scrap_values()
        vals.pop("operator_id", None)
        stock_scrap = self.StockScrap.create(vals)
        self.assertEqual(stock_scrap.operator_id, self.env.user)

    def test_01(self):
        """
        Data:
            Nope
        Test case:
            Create a scrap with operator
        Expected result:
            The operator must be set to the given operator
        """
        vals = self._get_scrap_values()
        vals["operator_id"] = self.demo_user.id
        stock_scrap = self.StockScrap.create(vals)
        self.assertNotEqual(self.demo_user, self.env.user)
        self.assertEqual(stock_scrap.operator_id, self.demo_user)
