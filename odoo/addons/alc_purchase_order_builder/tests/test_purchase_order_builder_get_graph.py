# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import datetime

from freezegun import freeze_time

from odoo.fields import Command
from odoo.tests import TransactionCase


class TestPurchaseOrderBuilder(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_obj = cls.env["product.product"]
        cls.purchase_obj = cls.env["purchase.order"]
        cls.partner = cls.env["res.partner"].create({"name": "Partner"})
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.product = cls.product_obj.create(
            {
                "name": "Product 1",
                "type": "product",
            }
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.product, cls.warehouse.lot_stock_id, 10.0
        )
        cls.sales = cls.env["sale.order"]
        for month in range(1, 14):
            sale = cls._add_done_sale_order(product=cls.product, qty=month)
            sale.action_done()
            sale.date_order = datetime.datetime(
                2023 + month // 13, month % 12 or 12, 15, 0, 0, 0
            )
            cls.sales |= sale

    @classmethod
    def _add_done_sale_order(
        cls, partner=None, product=None, qty=10, picking_policy="direct"
    ):
        if partner is None:
            partner = cls.partner
        warehouse = cls.warehouse
        sale_order_model = cls.env["sale.order"]
        lines = [
            Command.create(
                {
                    "name": p.name,
                    "product_id": p.id,
                    "product_uom_qty": qty,
                    "product_uom": p.uom_id.id,
                    "price_unit": 1,
                },
            )
            for p in product
        ]
        so_values = {
            "partner_id": partner.id,
            "warehouse_id": warehouse.id,
            "order_line": lines,
        }
        if picking_policy:
            so_values["picking_policy"] = picking_policy
        so = sale_order_model.create(so_values)
        so.action_confirm()
        so.action_done()
        return so

    @freeze_time("2024-01-15 15:15:15")
    def test_get_graph_values(self):
        graph_data = self.product.get_graph_values()
        graph_labels = [value["label"] for value in graph_data]
        graph_values = [value["value"] for value in graph_data]
        # First and last labels are dates, the first one start the same day as today
        # while the last one ends the day before today. We have 13 data.
        # As today is the 15th and as the sale orders dates are on the 15, the one from 01/23 is
        # taken into account while the one from 01/24 isn't.
        self.assertListEqual(
            graph_labels,
            [
                "15/1/23",
                "2/23",
                "3/23",
                "4/23",
                "5/23",
                "6/23",
                "7/23",
                "8/23",
                "9/23",
                "10/23",
                "11/23",
                "12/23",
                "14/1/24",
            ],
        )
        self.assertListEqual(
            graph_values,
            [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 0],
        )

    @freeze_time("2024-01-16 15:15:15")
    def test_get_graph_values_2(self):
        graph_data = self.product.get_graph_values()
        graph_labels = [value["label"] for value in graph_data]
        graph_values = [value["value"] for value in graph_data]
        # First and last labels are dates, the first one start the same day as today
        # while the last one ends the day before today. We have 13 data.
        # As today is the 16th and as the sale orders dates are on the 15, the one from 01/23 is
        # not taken into account while the one from 01/24 is.
        self.assertListEqual(
            graph_labels,
            [
                "16/1/23",
                "2/23",
                "3/23",
                "4/23",
                "5/23",
                "6/23",
                "7/23",
                "8/23",
                "9/23",
                "10/23",
                "11/23",
                "12/23",
                "15/1/24",
            ],
        )
        self.assertListEqual(
            graph_values,
            [0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0],
        )

    @freeze_time("2024-01-1 15:15:15")
    def test_get_graph_values_today_first_day_of_month(self):
        graph_data = self.product.get_graph_values()
        graph_labels = [value["label"] for value in graph_data]
        graph_values = [value["value"] for value in graph_data]
        # All the labels are month and only the data of the last 12 month are taken.
        self.assertListEqual(
            graph_labels,
            [
                "1/23",
                "2/23",
                "3/23",
                "4/23",
                "5/23",
                "6/23",
                "7/23",
                "8/23",
                "9/23",
                "10/23",
                "11/23",
                "12/23",
            ],
        )
        self.assertListEqual(
            graph_values,
            [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0],
        )
