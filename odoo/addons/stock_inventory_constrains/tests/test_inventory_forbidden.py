# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError
from odoo.tests.common import SavepointCase


class TestActAsView(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestActAsView, cls).setUpClass()
        cls.location = cls.env.ref("stock.stock_location_stock")

    def _create_inventory(self, location):
        return self.env["stock.inventory"].create(
            {"name": "Test Inventory", "filter": "none", "location_id": location.id}
        )

    def test_inventory_allowed(self):
        """ If the flag is_inventory_forbidden is not set on the stock.location, we can create a stock.inventory with 'all products'"""
        self.assertTrue(self._create_inventory(self.location))

    def test_inventory_forbidden(self):
        """ If the flag is_inventory_forbidden is set on the stock.location, we cannot create a stock.inventory with 'all products'"""
        self.location.is_inventory_forbidden = True
        with self.assertRaises(ValidationError):
            self._create_inventory(self.location)
