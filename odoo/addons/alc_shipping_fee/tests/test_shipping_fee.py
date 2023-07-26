# Copyright 2017-2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.fields import Command

from .common import TestShippingFeeCommon


class TestShippingFee(TestShippingFeeCommon):
    def test_customer_never_pay_fees(self):
        """Test a customer that should never pay shipping fees."""
        self.partner1.help_with_fee = False
        self.so1.action_confirm()
        self.so1.picking_ids.assign_release_channel()
        self.do_picking(self.so1.picking_ids)
        self.assertTrue(self.no_shipping_line_present(self.so1))

    def test_2_so_all_delivered_small_amount(self):
        """2 sale order for a small amount all delivered add fee."""
        self.so1.action_confirm()
        self.so2.action_confirm()
        self.so2.picking_ids.assign_release_channel()
        self.so1.picking_ids.assign_release_channel()
        self.do_picking(self.so2.picking_ids)
        self.do_picking(self.so1.picking_ids)
        self.assertTrue(self.no_shipping_line_present(self.so1))
        self.assertEqual(self.get_shipping_cost(self.so2), self.fee)
        self.assertEqual(
            self.product_used_for_cost_so_line(self.so2), self.so2.carrier_id.product_id
        )

    def test_2_so_all_delivered_large_amount(self):
        """2 sale order completely delivered large amount no fee."""
        self.so2.order_line[0].price_unit = 10
        self.so1.action_confirm()
        self.so2.action_confirm()
        self.so2.picking_ids.assign_release_channel()
        self.so1.picking_ids.assign_release_channel()
        self.do_picking(self.so2.picking_ids)
        self.do_picking(self.so1.picking_ids)
        self.assertTrue(self.no_shipping_line_present(self.so1))

    def test_3_so_in_2_delivery_fee_twice(self):
        """Two deliveries both with fee.

        The customer makes so1 (50 EUR) and so2 (30 EUR)
        Delivery 1: so1 and 20% of so2 -> fees
        The customer makes so3 (70 EUR)
        Delivery 2: 80% so2 and so3 -> fees
        """
        self.so1.action_confirm()
        self.so1.picking_ids.assign_release_channel()
        self.so2.order_line[0].price_unit = 6
        self.so2.write(
            {
                "order_line": [
                    Command.create(
                        {
                            "name": self.p3.name,
                            "product_id": self.p3.id,
                            "product_uom": self.ref("uom.product_uom_unit"),
                            "product_uom_qty": 1,
                            "price_unit": 24,
                        },
                    )
                ]
            }
        )
        self.so2.action_confirm()
        # First delivery : 100 % sale order 1 + 20 % sale order 2
        pick = self.so2.picking_ids
        pick.assign_release_channel()
        op = pick.move_line_ids
        op = op.filtered(lambda r: r.product_id.id == self.p1.id)
        op.write({"qty_done": 1})
        pick.button_validate()
        self.do_picking(self.so1.picking_ids)
        self.assertTrue(self.no_shipping_line_present(self.so1))
        self.assertEqual(self.get_shipping_cost(self.so2), self.fee)
        # Second delivery round
        # Create a 3rd sale order
        so3 = self.env["sale.order"].create(
            {
                "partner_id": self.partner1.id,
                "carrier_id": self.delivery_method.id,
                "order_line": [
                    Command.create(
                        {
                            "name": self.p1.name,
                            "product_id": self.p1.id,
                            "product_uom": self.ref("uom.product_uom_unit"),
                            "product_uom_qty": 1,
                            "price_unit": 70,
                        },
                    )
                ],
            }
        )
        so3.action_confirm()
        so3.picking_ids.assign_release_channel()
        pick = self.so2.picking_ids.filtered(lambda r: r.state != "done")
        pick.assign_release_channel()
        pick.action_assign()
        op = pick.move_line_ids
        op.write({"qty_done": 1})

        pick.button_validate()
        self.do_picking(so3.picking_ids)
        self.assertEqual(self.get_shipping_cost(self.so2), self.fee)
        self.assertEqual(self.get_shipping_cost(so3), self.fee)
        self.assertEqual(
            self.product_used_for_cost_so_line(so3), so3.carrier_id.product_id
        )

    def test_3_so_in_2_delivery_fee_once(self):
        """Two deliveries one without fees the other one with it.

        The customer makes so1 (100 EUR) and so2 (30 EUR)
        Delivery 1: so1 and 20% of so2 -> no fees
        The customer makes so3 (70 EUR)
        Delivery 2: 80% so2 and so3 -> fees
        """
        self.so1.order_line[0].price_unit = 100
        self.so1.action_confirm()
        self.so1.picking_ids.assign_release_channel()
        self.so2.order_line[0].price_unit = 6
        self.so2.write(
            {
                "order_line": [
                    Command.create(
                        {
                            "name": self.p3.name,
                            "product_id": self.p3.id,
                            "product_uom": self.ref("uom.product_uom_unit"),
                            "product_uom_qty": 1,
                            "price_unit": 24,
                        },
                    )
                ]
            }
        )
        self.so2.action_confirm()
        # First delivery : 100 % sale order 1 + 20 % sale order 2
        pick = self.so2.picking_ids
        pick.assign_release_channel()
        op = pick.move_line_ids
        op = op.filtered(lambda r: r.product_id.id == self.p1.id)
        op.write({"qty_done": 1})
        # Create a 3rd sale order
        # we create in draft in advance, to check it isn't messed with by the delivery
        so3 = self.env["sale.order"].create(
            {
                "partner_id": self.partner1.id,
                "carrier_id": self.delivery_method.id,
                "order_line": [
                    Command.create(
                        {
                            "name": self.p1.name,
                            "product_id": self.p1.id,
                            "product_uom": self.ref("uom.product_uom_unit"),
                            "product_uom_qty": 1,
                            "price_unit": 70,
                        },
                    )
                ],
            }
        )
        pick.button_validate()
        self.do_picking(self.so1.picking_ids)
        self.assertTrue(self.no_shipping_line_present(self.so1))
        self.assertTrue(self.no_shipping_line_present(self.so2))

        # this is already covered by the fact that if it was true for so3,
        # then no fee would be added on it afterwards. Still, it's better to be
        # explicit, and refactor this test if implementation changes
        (self.so1 | self.so2).invalidate_recordset()
        self.assertTrue(self.so1.used_for_delivery_fee)
        self.assertTrue(self.so2.used_for_delivery_fee)
        self.assertFalse(so3.used_for_delivery_fee)

        # Second delivery round
        so3.action_confirm()
        so3.picking_ids.assign_release_channel()
        pick = self.so2.picking_ids.filtered(lambda r: r.state != "done")
        pick.assign_release_channel()
        pick.action_assign()
        op = pick.move_line_ids
        op.write({"qty_done": 1})

        pick.button_validate()
        self.do_picking(so3.picking_ids)
        self.assertTrue(self.no_shipping_line_present(self.so2))
        self.assertEqual(self.get_shipping_cost(so3), self.fee)

    def test_3_so_in_2_delivery_fee_twice_2(self):
        """Two deliveries both with fee.

        The customer makes so1 (100 EUR) and so2 (30 EUR)
        Delivery 1: so1 and 20% of so2 -> no fees
        The customer makes so3 (70 EUR)
        Delivery 2: 80% so2 and so3 -> fees
        """
        self.so1.action_confirm()
        self.so1.picking_ids.assign_release_channel()
        self.so2.order_line[0].price_unit = 30
        self.so2.action_confirm()
        # First delivery : 100 % sale order 1 + 0 % sale order 2
        self.do_picking(self.so1.picking_ids)
        self.assertEqual(self.get_shipping_cost(self.so1), self.fee)
        self.assertTrue(self.no_shipping_line_present(self.so2))

        # Second delivery round
        # Create a 3rd sale order
        so3 = self.env["sale.order"].create(
            {
                "partner_id": self.partner1.id,
                "carrier_id": self.delivery_method.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": self.p1.name,
                            "product_id": self.p1.id,
                            "product_uom": self.ref("uom.product_uom_unit"),
                            "product_uom_qty": 1,
                            "price_unit": 70,
                        },
                    )
                ],
            }
        )
        so3.action_confirm()
        so3.picking_ids.assign_release_channel()
        self.so2.picking_ids.assign_release_channel()
        self.do_picking(so3.picking_ids)
        self.do_picking(self.so2.picking_ids)
        self.assertTrue(self.no_shipping_line_present(self.so2))
        self.assertEqual(self.get_shipping_cost(so3), self.fee)

    def test_3_so_in_2_delivery_fee_once_2(self):
        """Two deliveries one without fees the other one with it.

        The customer makes so1 (100 EUR) and so2 (30 EUR)
        Delivery 1: so1 and 0% of so2 -> no fees
        The customer makes so3 (70 EUR)
        Delivery 2: so2 and so3 -> fees
        """
        self.so1.order_line[0].price_unit = 100
        self.so1.action_confirm()
        self.so1.picking_ids.assign_release_channel()
        self.so2.order_line[0].price_unit = 30
        self.so2.action_confirm()
        # First delivery
        self.do_picking(self.so1.picking_ids)
        self.assertTrue(self.no_shipping_line_present(self.so1))
        self.assertTrue(self.no_shipping_line_present(self.so2))
        # Second delivery round
        # Create a 3rd sale order
        so3 = self.env["sale.order"].create(
            {
                "partner_id": self.partner1.id,
                "carrier_id": self.delivery_method.id,
                "order_line": [
                    Command.create(
                        {
                            "name": self.p1.name,
                            "product_id": self.p1.id,
                            "product_uom": self.ref("uom.product_uom_unit"),
                            "product_uom_qty": 1,
                            "price_unit": 70,
                        },
                    )
                ],
            }
        )
        so3.action_confirm()
        so3.picking_ids.assign_release_channel()
        self.so2.picking_ids.assign_release_channel()
        self.do_picking(so3.picking_ids)
        self.do_picking(self.so2.picking_ids)
        self.assertTrue(self.no_shipping_line_present(self.so2))
        self.assertEqual(self.get_shipping_cost(so3), self.fee)

    def test_no_shipping_fees(self):
        """Small order in round but second so with large amount."""
        # Create a second sale order for partner One
        self.so2 = self.env["sale.order"].create(
            {
                "partner_id": self.partner1.id,
                "carrier_id": self.delivery_method.id,
                "order_line": [
                    Command.create(
                        {
                            "name": self.p1.name,
                            "product_id": self.p1.id,
                            "product_uom": self.ref("uom.product_uom_unit"),
                            "product_uom_qty": 3,
                            "price_unit": 200,
                        },
                    )
                ],
            }
        )
        self.so2.action_confirm()
        self.so1.action_confirm()
        self.so1.picking_ids.assign_release_channel()
        self.do_picking(self.so1.picking_ids)
        self.assertTrue(self.no_shipping_line_present(self.so1))

    def test_multiple_customer_in_round(self):
        """2 customer in round, only partner 1 get charged."""
        self.so1.action_confirm()
        self.so2.action_confirm()
        so21 = self.env["sale.order"].create(
            {
                "partner_id": self.partner2.id,
                "carrier_id": self.delivery_method.id,
                "order_line": [
                    Command.create(
                        {
                            "name": self.p1.name,
                            "product_id": self.p1.id,
                            "product_uom": self.ref("uom.product_uom_unit"),
                            "product_uom_qty": 1,
                            "price_unit": 1000,
                        },
                    )
                ],
            }
        )
        so21.action_confirm()
        so21.picking_ids.assign_release_channel()
        self.so2.picking_ids.assign_release_channel()
        self.so1.picking_ids.assign_release_channel()
        self.do_picking(so21.picking_ids)
        self.do_picking(self.so2.picking_ids)
        self.do_picking(self.so1.picking_ids)
        self.assertTrue(self.no_shipping_line_present(self.so1))
        self.assertEqual(self.get_shipping_cost(self.so2), self.fee)
        self.assertTrue(self.no_shipping_line_present(so21))

    def test_one_customer_two_delivery_carrier(self):
        """1 customer 2 sale orders with 2 delivery carrier.

        He get charged twice.
        """
        self.so1.action_confirm()
        self.so2.carrier_id = self.delivery_method_2
        self.so2.order_line[0].price_unit = 170
        self.so2.action_confirm()
        self.so1.picking_ids.assign_release_channel()
        self.so2.picking_ids.assign_release_channel()
        self.do_picking(self.so1.picking_ids)
        self.do_picking(self.so2.picking_ids)
        self.assertEqual(self.get_shipping_cost(self.so1), self.fee)
        self.assertEqual(self.get_shipping_cost(self.so2), self.fee_2)

    def test_no_shipping_fees_no_specific_calc(self):
        """Order shouldn't have a fee and return in _add_delivery_cost_to_so."""
        # Create a second sale order for partner One
        self.so2 = self.env["sale.order"].create(
            {
                "partner_id": self.partner1.id,
                "carrier_id": self.delivery_method_3.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": self.p1.name,
                            "product_id": self.p1.id,
                            "product_uom": self.ref("uom.product_uom_unit"),
                            "product_uom_qty": 5,
                            "price_unit": 200,
                        },
                    )
                ],
            }
        )
        self.so2.action_confirm()
        self.so2.picking_ids.assign_release_channel()
        self.do_picking(self.so2.picking_ids)
        self.assertTrue(self.no_shipping_line_present(self.so2))

    def test_shipping_fees_no_specific_calc(self):
        """Order should have a fee and pass through _add_delivery_cost_to_so."""
        self.delivery_method_3.invoice_policy = "real"
        # Create a second sale order for partner One
        self.so2 = self.env["sale.order"].create(
            {
                "partner_id": self.partner1.id,
                "carrier_id": self.delivery_method_3.id,
                "order_line": [
                    Command.create(
                        {
                            "name": self.p1.name,
                            "product_id": self.p1.id,
                            "product_uom": self.ref("uom.product_uom_unit"),
                            "product_uom_qty": 1,
                            "price_unit": 10,
                        },
                    )
                ],
            }
        )
        self.so2.action_confirm()
        self.so2.picking_ids.assign_release_channel()
        self.do_picking(self.so2.picking_ids)
        self.assertEqual(self.get_shipping_cost(self.so2), self.fee_3)

    def test_avoid_shiping_cost(self):
        """If the outgoing picking type has avoid_shipping_cost at True.

        there should be no fee. Test with use_specific_cost_calculation
        and without.
        """
        new_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner2.id,
                "carrier_id": self.delivery_method.id,
                "order_line": [
                    Command.create(
                        {
                            "name": self.p1.name,
                            "product_id": self.p1.id,
                            "product_uom": self.ref("uom.product_uom_unit"),
                            "product_uom_qty": 1,
                            "price_unit": 10,
                        },
                    )
                ],
            }
        )
        new_order.action_confirm()
        new_order.picking_ids.assign_release_channel()
        self.do_picking(new_order.picking_ids)
        self.assertEqual(self.get_shipping_cost(new_order), self.fee)
        # Test with the same SO but we change the picking_type
        new_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner2.id,
                "carrier_id": self.delivery_method.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": self.p1.name,
                            "product_id": self.p1.id,
                            "product_uom": self.ref("uom.product_uom_unit"),
                            "product_uom_qty": 1,
                            "price_unit": 10,
                        },
                    )
                ],
            }
        )
        new_order.action_confirm()
        picking_type = new_order.picking_ids.filtered(
            lambda rec: rec.picking_type_code == "outgoing"
        ).mapped("picking_type_id")
        picking_type.avoid_shipping_cost = True
        new_order.picking_ids.assign_release_channel()
        self.do_picking(new_order.picking_ids)
        self.assertTrue(self.no_shipping_line_present(new_order))
        # Test with the delivery method 3 (With
        # use_specific_cost_calculation set to False)
        new_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner2.id,
                "carrier_id": self.delivery_method_3.id,
                "order_line": [
                    Command.create(
                        {
                            "name": self.p1.name,
                            "product_id": self.p1.id,
                            "product_uom": self.ref("uom.product_uom_unit"),
                            "product_uom_qty": 1,
                            "price_unit": 10,
                        },
                    )
                ],
            }
        )
        new_order.action_confirm()
        new_order.picking_ids.assign_release_channel()
        self.do_picking(new_order.picking_ids)
        self.assertTrue(self.no_shipping_line_present(new_order))

    def test_only_fixed_fee(self):
        self.partner3.help_with_fee = False
        so3 = self.env["sale.order"].create(
            {
                "partner_id": self.partner3.id,
                "carrier_id": self.delivery_method_4.id,
                "order_line": [
                    Command.create(
                        {
                            "name": self.p1.name,
                            "product_id": self.p1.id,
                            "product_uom": self.ref("uom.product_uom_unit"),
                            "product_uom_qty": 1,
                            "price_unit": 70,
                        },
                    )
                ],
            }
        )
        so3.action_confirm()
        so3.picking_ids.assign_release_channel()
        self.do_picking(so3.picking_ids)
        self.assertEqual(self.get_shipping_cost(so3), self.fixed_fee)

    def test_only_fixed_fee_even_though_help_with_fees(self):
        so3 = self.env["sale.order"].create(
            {
                "partner_id": self.partner3.id,
                "carrier_id": self.delivery_method_4.id,
                "order_line": [
                    Command.create(
                        {
                            "name": self.p1.name,
                            "product_id": self.p1.id,
                            "product_uom": self.ref("uom.product_uom_unit"),
                            "product_uom_qty": 1,
                            "price_unit": 70,
                        },
                    )
                ],
            }
        )
        so3.action_confirm()
        so3.picking_ids.assign_release_channel()
        self.do_picking(so3.picking_ids)
        self.assertEqual(self.get_shipping_cost(so3), self.fixed_fee)

    def test_fixed_and_extra_fees(self):
        so3 = self.env["sale.order"].create(
            {
                "partner_id": self.partner3.id,
                "carrier_id": self.delivery_method_5.id,
                "order_line": [
                    Command.create(
                        {
                            "name": self.p1.name,
                            "product_id": self.p1.id,
                            "product_uom": self.ref("uom.product_uom_unit"),
                            "product_uom_qty": 1,
                            "price_unit": 70,
                        },
                    )
                ],
            }
        )
        so3.action_confirm()
        so3.picking_ids.assign_release_channel()
        self.do_picking(so3.picking_ids)
        self.assertEqual(self.get_shipping_cost(so3), self.fixed_fee + self.fee)

    def test_extra_fee_only(self):
        so3 = self.env["sale.order"].create(
            {
                "partner_id": self.partner3.id,
                "carrier_id": self.delivery_method.id,
                "order_line": [
                    Command.create(
                        {
                            "name": self.p1.name,
                            "product_id": self.p1.id,
                            "product_uom": self.ref("uom.product_uom_unit"),
                            "product_uom_qty": 1,
                            "price_unit": 70,
                        },
                    )
                ],
            }
        )
        so3.action_confirm()
        so3.picking_ids.assign_release_channel()
        self.do_picking(so3.picking_ids)
        self.assertEqual(self.get_shipping_cost(so3), self.fee)

    def test_shipping_costs_twice_at_bo(self):

        product = self.env["product.product"].create(
            {
                "name": "Unittest product out of stock",
                "uom_id": self.env.ref("uom.product_uom_unit").id,
                "type": "product",
            }
        )
        so = self.env["sale.order"].create(
            {
                "partner_id": self.partner3.id,
                "carrier_id": self.delivery_method_5.id,
                "order_line": [
                    Command.create(
                        {
                            "name": self.p1.name,
                            "product_id": self.p1.id,
                            "product_uom": self.ref("uom.product_uom_unit"),
                            "product_uom_qty": 5,
                            "price_unit": 5,
                        },
                    ),
                    Command.create(
                        {
                            "name": product.name,
                            "product_id": product.id,
                            "product_uom": self.ref("uom.product_uom_unit"),
                            "product_uom_qty": 15,
                            "price_unit": 1,
                        },
                    ),
                ],
            }
        )

        so.action_confirm()
        pick = so.picking_ids
        pick.assign_release_channel()
        pick.picking_type_id.create_backorder = "always"
        self.do_picking(pick)
        self.assertEqual(self.get_shipping_cost(so), self.fixed_fee + self.fee)

        bo = self.env["stock.picking"].search([("backorder_id", "=", pick[0].id)])
        self._create_inventory(product, 100)
        bo.action_assign()
        bo.assign_release_channel()
        self.do_picking(bo)
        # Check shipping cost are not considered twice
        self.assertEqual(self.get_shipping_cost(so), self.fixed_fee + self.fee)

    def test_shipping_costs_twice_at_bo_and_new_so(self):

        product = self.env["product.product"].create(
            {
                "name": "Unittest product out of stock",
                "uom_id": self.env.ref("uom.product_uom_unit").id,
                "type": "product",
            }
        )
        so = self.env["sale.order"].create(
            {
                "partner_id": self.partner3.id,
                "carrier_id": self.delivery_method_5.id,
                "order_line": [
                    Command.create(
                        {
                            "name": self.p1.name,
                            "product_id": self.p1.id,
                            "product_uom": self.ref("uom.product_uom_unit"),
                            "product_uom_qty": 5,
                            "price_unit": 5,
                        },
                    ),
                    Command.create(
                        {
                            "name": product.name,
                            "product_id": product.id,
                            "product_uom": self.ref("uom.product_uom_unit"),
                            "product_uom_qty": 15,
                            "price_unit": 1,
                        },
                    ),
                ],
            }
        )

        so.action_confirm()
        pick = so.picking_ids
        pick.assign_release_channel()
        pick.picking_type_id.create_backorder = "always"
        self.do_picking(pick)
        self.assertEqual(self.get_shipping_cost(so), self.fixed_fee + self.fee)

        bo = self.env["stock.picking"].search([("backorder_id", "=", pick[0].id)])
        self._create_inventory(product, 100)

        so1 = self.env["sale.order"].create(
            {
                "partner_id": self.partner3.id,
                "carrier_id": self.delivery_method_5.id,
                "order_line": [
                    Command.create(
                        {
                            "name": self.p1.name,
                            "product_id": self.p1.id,
                            "product_uom": self.ref("uom.product_uom_unit"),
                            "product_uom_qty": 1,
                            "price_unit": 20,
                        },
                    )
                ],
            }
        )
        so1.action_confirm()
        so1.picking_ids.assign_release_channel()
        bo.action_assign()
        bo.assign_release_channel()
        self.do_picking(so1.picking_ids)
        self.do_picking(bo)

        self.assertEqual(self.get_shipping_cost(so1), self.fixed_fee + self.fee)
        # Check shipping cost are not considered twice
        self.assertEqual(self.get_shipping_cost(so), self.fixed_fee + self.fee)

    def test_3_so_in_one_delivery_no_fee_large_amount(self):

        so1 = self.env["sale.order"].create(
            {
                "partner_id": self.partner1.id,
                "carrier_id": self.delivery_method.id,
                "order_line": [
                    Command.create(
                        {
                            "name": self.p1.name,
                            "product_id": self.p1.id,
                            "product_uom": self.ref("uom.product_uom_unit"),
                            "product_uom_qty": 1,
                            "price_unit": 20,
                        },
                    )
                ],
            }
        )

        so2 = self.env["sale.order"].create(
            {
                "partner_id": self.partner1.id,
                "carrier_id": self.delivery_method.id,
                "order_line": [
                    Command.create(
                        {
                            "name": self.p1.name,
                            "product_id": self.p1.id,
                            "product_uom": self.ref("uom.product_uom_unit"),
                            "product_uom_qty": 12,
                            "price_unit": 20,
                        },
                    )
                ],
            }
        )
        so3 = self.env["sale.order"].create(
            {
                "partner_id": self.partner1.id,
                "carrier_id": self.delivery_method.id,
                "order_line": [
                    Command.create(
                        {
                            "name": self.p1.name,
                            "product_id": self.p1.id,
                            "product_uom": self.ref("uom.product_uom_unit"),
                            "product_uom_qty": 2,
                            "price_unit": 20,
                        },
                    )
                ],
            }
        )

        so1.action_confirm()
        so2.action_confirm()
        so3.action_confirm()
        so1.picking_ids.assign_release_channel()
        so2.picking_ids.assign_release_channel()
        so3.picking_ids.assign_release_channel()
        self.do_picking(so1.picking_ids)
        self.do_picking(so2.picking_ids)
        self.do_picking(so3.picking_ids)
        self.assertTrue(self.no_shipping_line_present(so1))
        self.assertTrue(self.no_shipping_line_present(so2))
        self.assertTrue(self.no_shipping_line_present(so3))

    def test_delivery_in_3_parts(self):
        product = self.env["product.product"].create(
            {
                "name": "Unittest product delivery several times",
                "uom_id": self.env.ref("uom.product_uom_unit").id,
                "type": "product",
            }
        )

        self._create_inventory(product, 5)
        so = self.env["sale.order"].create(
            {
                "partner_id": self.partner1.id,
                "carrier_id": self.delivery_method.id,
                "order_line": [
                    Command.create(
                        {
                            "name": product.name,
                            "product_id": product.id,
                            "product_uom": self.ref("uom.product_uom_unit"),
                            "product_uom_qty": 15,
                            "price_unit": 100,
                        },
                    ),
                ],
            }
        )

        so.action_confirm()
        pick = so.picking_ids
        pick.picking_type_id.create_backorder = "always"
        pick.assign_release_channel()
        self.do_picking(pick)
        self.assertTrue(self.no_shipping_line_present(so))

        bo = self.env["stock.picking"].search([("backorder_id", "=", pick[0].id)])
        self._create_inventory(product, 5)
        bo.action_assign()
        bo.assign_release_channel()
        self.do_picking(bo)
        self.assertTrue(self.no_shipping_line_present(so))

        bo2 = self.env["stock.picking"].search([("backorder_id", "=", bo.id)])
        self._create_inventory(product, 5)
        bo2.action_assign()
        bo2.assign_release_channel()
        self.do_picking(bo2)
        self.assertTrue(self.no_shipping_line_present(so))
