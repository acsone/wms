# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.fields import Date, Datetime
from odoo.tests.common import Form

from odoo.addons.base.tests.common import BaseCommon

to_date = Date.to_date
to_datetime = Datetime.to_datetime


class TestPurchaseOrderDatePlanned(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.supplier = cls.env.ref("base.res_partner_12")
        cls.product = cls.env["product.product"].create({"name": "Product 1"})
        cls.public_holiday = cls.env["hr.holidays.public"].create(
            {
                "year": 2017,
                "line_ids": [
                    Command.create({"name": "2 January", "date": "2017-01-02"}),
                    Command.create({"name": "9 January", "date": "2017-01-09"}),
                ],
            }
        )
        cls.supplierinfo_model = cls.env["product.supplierinfo"]
        cls.product = cls.env["product.product"].create({"name": "Product 1"})
        cls.seller = cls.supplierinfo_model.create(
            {
                "partner_id": cls.supplier.id,
                "min_qty": 0,
                "price": 100,
                "delay": 3,
                "product_tmpl_id": cls.product.product_tmpl_id.id,
            }
        )
        cls.po = cls.env["purchase.order"].create(
            {
                "partner_id": cls.supplier.id,
                "date_order": "2016-12-31",
                "order_line": [
                    Command.create(
                        {
                            "product_id": cls.product.id,
                            "name": cls.product.name,
                            "product_qty": 10,
                            "product_uom": cls.env.ref("uom.product_uom_unit").id,
                            "price_unit": 15,
                        }
                    )
                ],
            }
        )

    def _test_date_planned(self, seller, date_order, date_expected):
        pol = self.env["purchase.order.line"]
        _scheduled_date = pol._get_next_scheduled_date
        self.assertEqual(
            _scheduled_date(seller, to_date(date_order)), to_date(date_expected)
        )

    def test_get_next_scheduled_date(self):
        """
        Calendar:

        - 31 december 2017: Saturday
        - 1 january 2017: Sunday
        - 2 january 2017: Monday
        - 3 january 2017: Tuesday
        - 4 january 2017: Wednesday
        - 5 january 2017: Thursday
        - 6 january 2017: Friday
        - 7 january 2017: Saturday
        - 8 january 2017: Sunday
        :return:
        """
        # Try different date with a lead time of 3 days defined on the seller
        self._test_date_planned(self.seller, "2016-12-31", "2017-01-05")
        self._test_date_planned(self.seller, "2017-01-02", "2017-01-05")
        self._test_date_planned(self.seller, "2017-01-03", "2017-01-06")
        self._test_date_planned(self.seller, "2017-01-06", "2017-01-12")
        # Try with an empty seller and use the default lead time
        empty_seller = self.supplierinfo_model
        self._test_date_planned(empty_seller, "2016-12-31", "2016-12-31")

    def test_seller_delay(self):
        self.supplier.delivery_lead_time = 5
        seller_form = Form(self.supplierinfo_model)
        seller_form.partner_id = self.supplier
        self.assertEqual(seller_form.delay, 5)
        seller = seller_form.save()
        self.supplier.delivery_lead_time = 6
        self.assertEqual(seller.delay, 6)

        self.supplier.delivery_lead_time = False
        self.assertEqual(seller.delay, 6)

    def test_seller_delay_default(self):
        self.supplier.delivery_lead_time = 5
        seller_form = Form(
            self.supplierinfo_model.with_context(default_partner_id=self.supplier.id)
        )
        # seller_form.partner_id = self.supplier
        self.assertEqual(seller_form.delay, 5)
        seller = seller_form.save()
        self.supplier.delivery_lead_time = 6
        self.assertEqual(seller.delay, 6)

    def test_po_date_planned(self):
        """Test changing date planned on purchase order level."""
        self.assertEqual(self.po.date_planned, to_datetime("2017-01-05"))
        self.assertEqual(self.po.order_line.date_planned, to_datetime("2017-01-05"))
        self.po.order_line.date_planned = "2017-01-06"

        self.assertEqual(self.po.order_line.date_planned, to_datetime("2017-01-06"))

        self.po.date_planned = "2017-01-07"
        self.assertEqual(self.po.order_line.date_planned, to_datetime("2017-01-07"))
