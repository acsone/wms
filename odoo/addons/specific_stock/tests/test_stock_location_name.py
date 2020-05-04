# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.tests.common import SingleTransactionCase


class TestStockLocationName(SingleTransactionCase):
    def setUp(self):
        super(TestStockLocationName, self).setUp()

        self.model = self.env["stock.location"]
        self.location_base = self.model.create({"name": "Base", "usage": "internal"})
        self.location_1 = self.model.create(
            {
                "name": "One",
                "usage": "internal",
                "location_id": self.location_base.id,
                "act_as_view": False,
            }
        )

    def test_name_with_act_as_view(self):
        """Check the name generation of stock location."""
        # Standard behaviour
        self.assertEqual(self.location_1.name_get()[0][1], "Base/One")
        self.location_1.usage = "view"
        self.assertEqual(self.location_1.name_get()[0][1], "One")
        # Specific behaviour
        self.location_1.usage = "internal"
        self.location_1.act_as_view = True
        self.assertEqual(self.location_1.name_get()[0][1], "One")
        # Back to standard behaviour
        self.location_1.act_as_view = False
        self.assertEqual(self.location_1.name_get()[0][1], "Base/One")
