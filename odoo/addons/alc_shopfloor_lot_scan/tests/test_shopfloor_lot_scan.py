# Copyright 2023 ACSONE SA/NV (http://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.shopfloor.tests.test_actions_search import TestSearchBaseCase


class TestSearchCase(TestSearchBaseCase):
    def test_search_lot(self):
        record = self.env["stock.lot"].sudo().create({"product_id": self.product_a.id})
        identifier = f"#{record.product_id.default_code}#{record.name}"
        handler = self.search.lot_from_scan
        # scan only the lot barcode
        self.assertEqual(handler(record.name), record)
        # scan alcyon lot barcode
        self.assertEqual(handler(identifier), record)
