# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.alc_pricelist_discount.tests.common import TestPricelistDiscountCommon


class TestPriceTripleDiscountExclusive(TestPricelistDiscountCommon):
    def test_price_triple_discount_exclusive(self):
        self.sol_p2._compute_discount_item_id()
        self.assertEqual(self.sol_p2.discount_item_id, self.discount_item)
        self.assertEqual(self.sol_p2.discount2, 10)
        self.discount_item.exclusive = True
        self.sol_p2.compute_supplier_promotion()
        self.assertEqual(self.sol_p2.discount_item_id, self.discount_item)
        self.assertEqual(self.sol_p2.discount2, 0)
