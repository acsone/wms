# -*- coding: utf-8 -*-
# Copyright 2019 Iryna Vyshnevska (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from .common import BaseCase


class TestStockMoveWizard(BaseCase):
    def setUp(self):
        super(TestStockMoveWizard, self).setUp()
        self.po_model = self.env["purchase.order"]
        self.wizard_obj = self.env["wizard.stock.move.update.handler"]

    def create_purchase_order(self, line_vals=None, products=None):
        if not products:
            products = [self.product_1, self.product_2]
        po = self.po_model.create({"partner_id": self.env.ref("base.res_partner_1").id})
        for product in products:
            values = {
                "product_id": product.id,
                "name": product.name,
                "date_planned": "2017-01-01 12:42:12",
                "product_qty": 12,
                "product_uom": product.uom_id.id,
                "price_unit": 42,
                "order_id": po.id,
            }
            if line_vals:
                values.update(line_vals)
            po.order_line.create(values)
        return po

    def force_picking(self, picking):
        picking.action_assign()
        pack_operation = picking.pack_operation_product_ids
        for pack in pack_operation:
            qty = pack.product_qty
            pack.write(
                {
                    "pack_lot_ids": [
                        (
                            0,
                            0,
                            {
                                "life_date": fields.Datetime.now(),
                                "lot_name": "20170102",
                                "qty": qty,
                            },
                        )
                    ],
                    "qty_done": qty,
                }
            )
        picking.do_transfer()

    def test_stock_move_move(self):
        po_1 = self.create_purchase_order()
        po_2 = self.create_purchase_order({"date_planned": "2017-07-02 01:01:01"})
        po_1.button_confirm()
        po_2.button_confirm()
        pick_1 = po_1.picking_ids
        pick_2 = po_2.picking_ids

        self.assertEqual(len(pick_1.move_lines), 2)
        self.assertEqual(len(pick_2.move_lines), 2)
        self.assertEqual(po_1.order_line[0].qty_received, 0)
        self.assertEqual(po_1.order_line[1].qty_received, 0)
        target_move = pick_1.move_lines[0]
        self.assertEqual(target_move.date_expected, "2017-01-01 12:42:12")

        wizard = self.wizard_obj.new(
            {"move_id": target_move.id, "new_date_expected": "2017-07-02 12:30:00"}
        )
        wizard.action_set_expired_date()
        # after wizard run one move moved to other picking
        self.assertEqual(len(pick_1.move_lines), 1)
        self.assertEqual(len(pick_2.move_lines), 3)
        # impacted move get new expected date
        self.assertEqual(target_move.date_expected, "2017-07-02 12:30:00")
        self.force_picking(pick_2)
        # on receiving products from second pickind first purchase order
        # updated
        self.assertEqual(po_1.order_line[0].qty_received, 12)
        self.assertEqual(po_1.order_line[1].qty_received, 0)

    def test_stock_move_one_move(self):
        po_1 = self.create_purchase_order(products=self.product_1)
        po_1.button_confirm()
        pick_1 = po_1.picking_ids

        self.assertEqual(len(po_1.picking_ids), 1)
        self.assertEqual(len(pick_1.move_lines), 1)

        target_move = pick_1.move_lines[0]
        wizard = self.wizard_obj.new(
            {"move_id": target_move.id, "new_date_expected": "2017-07-02 12:30:00"}
        )
        wizard.action_set_expired_date()

        # as picking has only one move instad of creating new picking
        # current updated with new date
        self.assertEqual(po_1.picking_ids, pick_1)
        self.assertEqual(pick_1.min_date, "2017-07-02 12:30:00")
        self.assertEqual(target_move.date_expected, "2017-07-02 12:30:00")

    def test_stock_move_new_picking(self):
        po_1 = self.create_purchase_order()
        po_1.button_confirm()
        pick_1 = po_1.picking_ids

        # order has one picking each
        self.assertEqual(len(po_1.picking_ids), 1)
        self.assertEqual(len(pick_1.move_lines), 2)

        target_move = pick_1.move_lines[0]
        wizard = self.wizard_obj.new(
            {"move_id": target_move.id, "new_date_expected": "2017-07-02 12:30:00"}
        )
        wizard.action_set_expired_date()

        # we don't have appropriate picking for merging so new one created
        pick_2 = po_1.picking_ids - pick_1
        self.assertEqual(len(po_1.picking_ids), 2)
        self.assertEqual(len(pick_1.move_lines), 1)
        self.assertEqual(len(pick_2.move_lines), 1)
        self.assertEqual(pick_2.min_date, "2017-07-02 12:30:00")
        # impacted move get new expected date
        self.assertEqual(target_move.date_expected, "2017-07-02 12:30:00")

    def test_move_and_close_picking(self):
        po_1 = self.create_purchase_order(products=self.product_1)
        po_2 = self.create_purchase_order({"date_planned": "2017-07-02 01:01:01"})
        po_1.button_confirm()
        po_2.button_confirm()
        pick_1 = po_1.picking_ids
        pick_2 = po_2.picking_ids
        target_move = pick_1.move_lines[0]

        self.assertEqual(pick_1.state, "assigned")
        self.assertEqual(pick_2.state, "assigned")
        self.assertEqual(target_move.date_expected, "2017-01-01 12:42:12")

        wizard = self.wizard_obj.new(
            {"move_id": target_move.id, "new_date_expected": "2017-07-02 12:30:00"}
        )
        wizard.action_set_expired_date()

        # move moved to other picking, initial picking without moves canceled
        self.assertEqual(pick_1.state, "cancel")
        self.assertEqual(pick_2.state, "assigned")
        self.assertEqual(target_move.date_expected, "2017-07-02 12:30:00")
        self.assertEqual(len(pick_1.move_lines), 0)
        self.assertEqual(len(pick_2.move_lines), 3)

    def test_cancel_move(self):
        po = self.create_purchase_order()
        po.button_confirm()
        pick = po.picking_ids
        move_1 = pick.move_lines[0]
        move_2 = pick.move_lines - move_1
        self.assertEqual(pick.state, "assigned")
        self.assertEqual(move_1.state, "assigned")
        self.assertEqual(move_2.state, "assigned")

        move_1.action_cancel_move()
        self.assertEqual(pick.state, "assigned")
        self.assertEqual(move_1.state, "cancel")
        self.assertEqual(move_2.state, "assigned")

        move_2.action_cancel_move()
        self.assertEqual(pick.state, "cancel")
        self.assertEqual(move_1.state, "cancel")
        self.assertEqual(move_2.state, "cancel")
