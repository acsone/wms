# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import freezegun

from odoo.addons.alc_eshop_api_products_on_order.schemas import ProductOnOrder
from odoo.addons.alc_eshop_api_products_on_order.tests.common import ProductOnOrderCase


class TestProductOnOrder(ProductOnOrderCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.blanket_order = cls.sell(
            cls.product_ali, 3, "2020-01-02 14:00:00", confirm=False
        )
        cls.blanket_order.order_type = "blanket"
        cls.blanket_order.blanket_reservation_strategy = "at_call_off"
        cls.blanket_order.write(
            {
                "blanket_validity_start_date": "2020-01-02",
                "blanket_validity_end_date": "2021-01-02",
            }
        )
        cls._add_product_qty(cls.product_ali, 4)
        cls.blanket_order.action_confirm()

    @classmethod
    def get_blanket_product_on_order(cls):
        cls.env.flush_all()
        cls.env.invalidate_all()
        return cls.env["alc.eshop.product.on.order"].search(
            [("order_id", "=", cls.blanket_order.id)]
        )

    def test_cancel(self):
        with self._create_test_client(partner=self.partner_1) as test_client:
            response = test_client.post(
                f"/products_on_order/cancel/{self.so_ali_out_of_stock.order_line.id}",
                json={"quantity": 1},
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["status"], True)

    def test_cancel_no_back_order(self):
        with self._create_test_client(partner=self.partner_1) as test_client:
            response = test_client.post(
                f"/products_on_order/cancel/{self.so_medoc_in_stock.order_line.id}",
                json={"quantity": 1},
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["status"], False)

    def test_cancel_blanket_order_line_not_allowed(self):
        with self._create_test_client(partner=self.partner_1) as test_client:
            response = test_client.post(
                f"/products_on_order/cancel/{self.blanket_order.order_line.id}",
                json={"quantity": 1},
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["status"], False)

    def test_products_on_order(self):
        product_on_order = self.get_blanket_product_on_order()
        info: ProductOnOrder = ProductOnOrder.from_alc_eshop_product_on_order(
            product_on_order
        )
        self.assertEqual(info.qty_ordered, 3)
        self.assertEqual(info.qty_in_backorder, 3)

        with freezegun.freeze_time("2020-01-02 14:00:00"):
            call_off = self.env["sale.order"].create(
                {
                    "partner_id": self.partner_1.id,
                    "order_type": "call_off",
                    "blanket_order_id": self.blanket_order.id,
                    "order_line": [
                        (
                            0,
                            0,
                            {"product_id": self.product_ali.id, "product_uom_qty": 1},
                        )
                    ],
                }
            )
            call_off.action_confirm()
        product_on_order = self.get_blanket_product_on_order()
        info = ProductOnOrder.from_alc_eshop_product_on_order(product_on_order)
        self.assertEqual(info.qty_ordered, 3)
        self.assertEqual(info.qty_in_backorder, 2)

        # we now deliver the pickings
        picking = call_off.order_line.blanket_move_ids.picking_id
        picking.action_set_quantities_to_reservation()
        picking._action_done()

        # the qty ordered should be the remaining qty
        product_on_order = self.get_blanket_product_on_order()
        info = ProductOnOrder.from_alc_eshop_product_on_order(product_on_order)
        self.assertEqual(info.qty_ordered, 2)
        self.assertEqual(info.qty_in_backorder, 2)

        # we create a new call off for the remaining qty
        with freezegun.freeze_time("2020-01-02 14:00:00"):
            call_off = self.env["sale.order"].create(
                {
                    "partner_id": self.partner_1.id,
                    "order_type": "call_off",
                    "blanket_order_id": self.blanket_order.id,
                    "order_line": [
                        (
                            0,
                            0,
                            {"product_id": self.product_ali.id, "product_uom_qty": 2},
                        )
                    ],
                }
            )
            call_off.action_confirm()

        # no more product to order -> no backorder
        product_on_order = self.get_blanket_product_on_order()
        info = ProductOnOrder.from_alc_eshop_product_on_order(product_on_order)
        self.assertEqual(info.qty_ordered, 2)
        self.assertEqual(info.qty_in_backorder, 0)

        # we process the call off
        picking = call_off.order_line.blanket_move_ids.picking_id
        picking.action_set_quantities_to_reservation()
        picking._action_done()

        # we should no more have any product on order
        product_on_order = self.get_blanket_product_on_order()
        self.assertFalse(product_on_order)
