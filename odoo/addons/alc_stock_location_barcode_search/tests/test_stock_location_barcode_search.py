# -*- coding: utf-8 -*-
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestStockLocationBarcodeSearch(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestStockLocationBarcodeSearch, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.env["stock.location"].search([]).write({"active": False})
        cls.stock_location_123 = cls.env["stock.location"].create(
            {"name": "one two three", "barcode": "#123"}
        )
        cls.stock_location_456 = cls.env["stock.location"].create(
            {"name": "four five six", "barcode": "#456"}
        )

    def test_name_search(self):
        self.assertEqual(
            self.env["stock.location"].name_search("#123"),
            [(self.stock_location_123.id, self.stock_location_123.display_name)],
        )
        self.assertEqual(
            self.env["stock.location"].name_search("#456"),
            [(self.stock_location_456.id, self.stock_location_456.display_name)],
        )
        self.assertFalse(self.env["stock.location"].name_search("#789"))
        self.assertEqual(
            self.env["stock.location"].name_search("one"),
            [(self.stock_location_123.id, self.stock_location_123.display_name)],
        )
        self.assertEqual(
            self.env["stock.location"].name_search("five"),
            [(self.stock_location_456.id, self.stock_location_456.display_name)],
        )
