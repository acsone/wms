# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestProductRouteMto(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.route_mto = cls.env.ref("stock.route_warehouse0_mto")
        cls.route_mto.active = True
        cls.product_with_order_point = cls.env["product.product"].create(
            {
                "name": "Product Test",
                "type": "product",
                "orderpoint_ids": [
                    (
                        0,
                        0,
                        {
                            "product_min_qty": 1,
                            "product_max_qty": 10,
                            "location_id": cls.env.ref("stock.stock_location_stock").id,
                            "product_uom": cls.env.ref("uom.product_uom_unit").id,
                        },
                    )
                ],
            }
        )
        cls.product_no_route = cls.env["product.product"].create(
            {
                "name": "Product Test",
                "type": "product",
            }
        )

    def test_create_product_mto(self):
        product = self.env["product.product"].create(
            {
                "name": "Product Test",
                "type": "product",
                "route_ids": [(4, self.route_mto.id)],
            }
        )
        self.assertTrue(product.orderpoint_ids)

    def test_update_product_no_orderpoint_with_route_mto(self):
        self.assertFalse(self.product_no_route.is_mto)
        self.assertFalse(self.product_no_route.orderpoint_ids)
        self.product_no_route.route_ids += self.route_mto
        self.assertTrue(self.product_no_route.is_mto)
        self.assertTrue(self.product_no_route.orderpoint_ids)

    def test_update_product_with_orderpoint_with_route_mto(self):
        self.assertFalse(self.product_with_order_point.is_mto)
        self.assertTrue(self.product_with_order_point.orderpoint_ids)
        original_orderpoint = self.product_with_order_point.orderpoint_ids
        self.product_with_order_point.route_ids += self.route_mto
        self.assertTrue(self.product_with_order_point.is_mto)
        self.assertEqual(
            self.product_with_order_point.orderpoint_ids, original_orderpoint
        )

    def test_create_template_mto(self):
        template = self.env["product.template"].create(
            {
                "name": "Product Test",
                "type": "product",
                "route_ids": [(4, self.route_mto.id)],
            }
        )
        self.assertTrue(template.is_mto)
        self.assertTrue(template.product_variant_ids.is_mto)
        self.assertTrue(template.product_variant_ids.orderpoint_ids)
