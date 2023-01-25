# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.alc_pricelist_discount.tests.common import PricelistDiscountCase


class TestAlcSaleOrderPriceRecalculation(PricelistDiscountCase):
    def test_price_recalculation(self):
        # at this stage we have two sale order line
        # one with discount2 and one with discount2 and discount3 set
        self.assertEqual(100, self.sol_p1.price_unit)
        self.assertEqual(10, self.sol_p1.discount2)
        self.assertEqual(0, self.sol_p1.discount3)
        self.assertEqual(90, self.sol_p1.price_subtotal)

        self.assertTrue(self.sol_p2.discount2)
        self.assertTrue(self.sol_p2.discount2)
        # if we set a date_start into the future on the supplier info of p1
        # and recompute the prices, the dicount2 on the first line will
        # be reset to 0
        self.supplierinfo1.write({"date_start": "2099-01-01", "date_end": "2100-01-01"})
        self.sale.recalculate_prices()
        self.assertEqual(100, self.sol_p1.price_unit)
        self.assertEqual(0, self.sol_p1.discount2)
        self.assertEqual(0, self.sol_p1.discount3)
        self.assertEqual(100, self.sol_p1.price_subtotal)

        # if set date_end to today on the supplier info of p2 and on the pricelist
        # for p2 and set the date_order to 2099-01-01 all the discounts on the line
        # 2 will be reset to 0 and the discount2 on line 1 will be set to 10
        self.supplierinfo2.write(
            {"date_start": fields.Date.today(), "date_end": fields.Date.today()}
        )
        self.discount_pricelist_id.item_ids.write(
            {"date_start": fields.Date.today(), "date_end": fields.Date.today()}
        )
        self.sale.date_order = "2099-01-01"
        self.sale.recalculate_prices()

        self.assertEqual(100, self.sol_p1.price_unit)
        self.assertEqual(10, self.sol_p1.discount2)
        self.assertEqual(0, self.sol_p1.discount3)
        self.assertEqual(90, self.sol_p1.price_subtotal)

        self.assertFalse(self.sol_p2.discount2)
        self.assertFalse(self.sol_p2.discount2)
