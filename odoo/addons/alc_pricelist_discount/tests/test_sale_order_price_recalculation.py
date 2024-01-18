# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import api, fields

from .common import TestPricelistDiscountCommon


class TestSaleOrderPriceRecalculation(TestPricelistDiscountCommon):
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
        self.sale.action_update_prices()
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
            {
                "date_start": fields.Date.today() - timedelta(days=1),
                "date_end": fields.Date.today(),
            }
        )
        self.sale.date_order = "2099-01-01"
        self.sale.action_update_prices()

        self.assertEqual(100, self.sol_p1.price_unit)
        self.assertEqual(10, self.sol_p1.discount2)
        self.assertEqual(0, self.sol_p1.discount3)
        self.assertEqual(90, self.sol_p1.price_subtotal)

        self.assertFalse(self.sol_p2.discount2)
        self.assertFalse(self.sol_p2.discount2)

    def test_recalculation_is_not_triggered_at_creation_through_call_kw(self):

        # Ensure that default behavior provides different discounts
        self.assertEqual(10, self.sol_p1.discount2)
        self.assertEqual(0, self.sol_p1.discount3)

        args = [
            {
                "__last_update": False,
                "partner_id": self.partner.id,
                "order_line": [
                    [
                        0,
                        "virtual_31",
                        {
                            "name": self.p1.name,
                            "product_id": self.p1.id,
                            "product_uom_qty": 1,
                            "product_uom": self.env.ref("uom.product_uom_unit").id,
                            "discount2": 5,
                            "discount3": 4,
                        },
                    ]
                ],
            }
        ]
        kwargs = {"context": self.env.context}

        SaleOrder = self.env["sale.order"]
        sale3_id = api.call_kw(SaleOrder, "create", args, kwargs)
        sale3 = SaleOrder.browse(sale3_id)

        self.assertEqual(5, sale3.order_line.discount2)
        self.assertEqual(4, sale3.order_line.discount3)
