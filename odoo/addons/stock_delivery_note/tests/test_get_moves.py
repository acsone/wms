# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from datetime import datetime

from odoo.tests.common import SavepointCase


class TestStockDeliveryNoteGetMoves(SavepointCase):
    @classmethod
    def _create_so(cls, product):
        so = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "suite_name": "123454321",
                "client_order_ref": "customer.ref.123",
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": product.name,
                            "product_id": product.id,
                            "product_uom": cls.env.ref("product.product_uom_unit").id,
                            "product_uom_qty": 10,
                            "price_unit": 50,
                            "tax_id": [(4, cls.tax.id, False)],
                        },
                    )
                ],
            }
        )
        so.action_confirm()
        reassign = so.picking_ids.filtered(
            lambda x: x.state == "confirmed"
            or ((x.state in ["partially_available", "waiting"]) and not x.printed)
        )
        if reassign:
            reassign.do_unreserve()
            reassign.action_assign()
        return so

    @classmethod
    def _prepare_shipping(cls, so, lot_name):
        picking = so.picking_ids
        picking.action_assign()
        pack_operation = picking.pack_operation_product_ids
        pack_operation.write(
            {
                "pack_lot_ids": [
                    (
                        0,
                        0,
                        {
                            "life_date": "2017-01-31 10:00:00",
                            "lot_name": lot_name,
                            "qty": 10,
                        },
                    )
                ],
                "qty_done": 10,
            }
        )
        return picking

    @classmethod
    def setUpClass(cls):
        super(TestStockDeliveryNoteGetMoves, cls).setUpClass()

        cls.smallyear = str(datetime.now().year)[2:]
        # Create a sale tax
        cls.tax = cls.env["account.tax"].create(
            {
                "tax_group_id": cls.env.ref("specific_data.vat_tax_group").id,
                "amount": 6,
                "name": "test_tax",
            }
        )
        # Create a couple of products
        cls.p1 = cls.env["product.product"].create(
            {
                "name": "Unittest P1",
                "default_code": "5173360",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "consu",
            }
        )
        cls.p2 = cls.env["product.product"].create(
            {
                "name": "Unittest P2",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
            }
        )
        cls.p3 = cls.env["product.product"].create(
            {
                "name": "Unittest P3",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
            }
        )
        # Add some stock for p1 and p2
        inventory = cls.env["stock.inventory"].create(
            {
                "name": "Test",
                "location_id": cls.env.ref("stock.stock_location_stock").id,
                "filter": "partial",
            }
        )
        inventory.prepare_inventory()
        cls.env["stock.inventory.line"].create(
            {
                "inventory_id": inventory.id,
                "product_id": cls.p1.id,
                "product_uom_id": cls.env.ref("product.product_uom_unit").id,
                "product_qty": 100,
                "location_id": cls.env.ref("stock.stock_location_stock").id,
            }
        )
        inventory.action_done()
        inventory = cls.env["stock.inventory"].create(
            {
                "name": "Test",
                "location_id": cls.env.ref("stock.stock_location_stock").id,
                "filter": "partial",
            }
        )
        inventory.prepare_inventory()
        cls.env["stock.inventory.line"].create(
            {
                "inventory_id": inventory.id,
                "product_id": cls.p2.id,
                "product_uom_id": cls.env.ref("product.product_uom_unit").id,
                "product_qty": 100,
                "location_id": cls.env.ref("stock.stock_location_stock").id,
            }
        )
        inventory.action_done()
        # Create the customer
        cls.partner = cls.env["res.partner"].create(
            {
                "title": cls.env.ref("base.res_partner_title_prof").id,
                "name": "HOENS OLIVIER",
                "email": "tester@pytest.com",
                "ref": "123456789",
                "street": "Rue Polisart 2 A",
                "zip": "5300",
                "city": "ANDENNE",
                "country_id": cls.env.ref("base.be").id,
            }
        )
        cls.so = cls._create_so(cls.p1)

    def test_no_delivery(self):
        picking = self._prepare_shipping(self.so, "20190101")
        res = picking.get_moves_by_order()
        self.assertEqual(len(res), 0)

    def test_one_shipping(self):
        picking = self._prepare_shipping(self.so, "20190101")
        picking.do_transfer()
        res = picking.get_moves_by_order()
        self.assertEqual(len(res), 1)
        order, all_moves = res[0]
        self.assertEqual(order, self.so)
        moves, _bo_moves = all_moves
        self.assertEqual(len(moves), 1)
        self.assertEqual(moves[0].product_qty, 10.0)

    def test_no_group_shipping(self):
        picking1 = self._prepare_shipping(self.so, "20190101")
        # create a second so
        so2 = self._create_so(self.p2)
        picking2 = self._prepare_shipping(so2, "20190102")
        picking2.do_transfer()
        (picking1 | picking2).do_transfer()
        # picking 1 and 2 are separated
        # thus only their own moves are shown
        res = picking1.get_moves_by_order()
        self.assertEqual(len(res), 1)
        order, all_moves = res[0]
        self.assertEqual(order, self.so)
        moves, bo_moves = all_moves
        self.assertEqual(len(moves), 1)
        self.assertEqual(len(bo_moves), 0)
        self.assertEqual(moves[0].product_qty, 10.0)

        res = picking2.get_moves_by_order()
        self.assertEqual(len(res), 1)
        order, all_moves = res[0]
        self.assertEqual(order, so2)
        moves, bo_moves = all_moves
        self.assertEqual(len(moves), 1)
        self.assertEqual(len(bo_moves), 0)
        self.assertEqual(moves[0].product_qty, 10.0)

    def test_sorted_by_date_order(self):
        self.so.date_order = "2020-02-20 20:02:20"
        picking1 = self._prepare_shipping(self.so, "20190101")
        picking1.picking_type_id.groupbypartner = True
        # purposely set dates
        # create a second so
        so2 = self._create_so(self.p2)
        so2.date_order = "2011-11-11 11:11:02"
        picking2 = self._prepare_shipping(so2, "20190102")
        self.assertEqual(picking1, picking2)
        picking1.do_transfer()
        res = picking2.get_moves_by_order()

        self.assertEqual(len(res), 2)
        order1, _all_moves1 = res[0]
        self.assertEqual(order1, so2)

        order2, _all_moves2 = res[1]
        self.assertEqual(order2, self.so)

    def test_group_shipping(self):
        picking1 = self._prepare_shipping(self.so, "20190101")
        picking1.picking_type_id.groupbypartner = True
        # create a second so
        so2 = self._create_so(self.p2)
        picking2 = self._prepare_shipping(so2, "20190102")
        self.assertEqual(picking1, picking2)
        picking1.do_transfer()
        res = picking2.get_moves_by_order()

        self.assertEqual(len(res), 2)
        order1, all_moves1 = res[0]
        self.assertEqual(order1, self.so)

        order2, all_moves2 = res[1]
        self.assertEqual(order2, so2)

        so1_moves, bo_moves = all_moves1
        self.assertEqual(len(bo_moves), 0)
        so2_moves, bo_moves = all_moves2
        self.assertEqual(len(bo_moves), 0)

        # moves are linked to right SO
        self.assertEqual(order1.order_line[0].product_id, so1_moves[0].product_id)
        self.assertEqual(order2.order_line[0].product_id, so2_moves[0].product_id)

    def test_group_shipping_with_bo(self):
        picking1 = self._prepare_shipping(self.so, "20190101")
        picking1.picking_type_id.groupbypartner = True
        # create a second so
        so2 = self._create_so(self.p2)
        # partial deliver
        picking2 = so2.picking_ids
        picking2.action_assign()
        picking2.do_prepare_partial()
        pack_operations = picking2.pack_operation_product_ids
        for pack_op in pack_operations:
            if pack_op.product_id == self.p1:
                lot_name = "20190101"
                pack_op.write(
                    {
                        "pack_lot_ids": [
                            (
                                0,
                                0,
                                {
                                    "life_date": "2019-01-31 10:00:00",
                                    "lot_name": lot_name,
                                    "qty": 10,
                                },
                            )
                        ],
                        "qty_done": 10,
                    }
                )
            elif pack_op.product_id == self.p2:
                lot_name = "20190102"
                pack_op.write(
                    {
                        "pack_lot_ids": [
                            (
                                0,
                                0,
                                {
                                    "life_date": "2019-01-31 10:00:00",
                                    "lot_name": lot_name,
                                    "qty": 2.0,
                                },
                            )
                        ],
                        "qty_done": 2.0,
                    }
                )
        self.assertEqual(picking1, picking2)
        shipping = picking1
        # do a partial delivery
        shipping.do_new_transfer()
        res = shipping.get_moves_by_order()

        self.assertEqual(len(res), 2)

        order1, all_moves1 = res[0]
        self.assertEqual(order1, self.so)

        order2, all_moves2 = res[1]
        self.assertEqual(order2, so2)

        so1_moves, so1_bo_moves = all_moves1
        self.assertEqual(len(so1_bo_moves), 0)
        so2_moves, so2_bo_moves = all_moves2
        self.assertEqual(len(so2_bo_moves), 1)

        # moves are linked to right SO
        self.assertEqual(order1.order_line[0].product_id, so1_moves[0].product_id)
        self.assertEqual(order2.order_line[0].product_id, so2_moves[0].product_id)
        self.assertEqual(order2.order_line[0].product_id, so2_bo_moves[0].product_id)
        self.assertEqual(so2_moves[0].product_qty, 2.0)
        self.assertEqual(so2_bo_moves[0].product_qty, 8.0)
