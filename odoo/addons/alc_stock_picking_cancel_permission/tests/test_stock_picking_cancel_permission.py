# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.fields import Command
from odoo.tests.common import TransactionCase


class TestStockPickingName(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.picking_cancel_group = cls.env.ref(
            "alc_stock_picking_cancel_permission.group_picking_cancel"
        )
        loc_stock = cls.env.ref("stock.stock_location_stock")
        loc_customer = cls.env.ref("stock.stock_location_customers")
        product_1 = cls.env["product.product"].create(
            {
                "name": "test product 1",
                "type": "product",
                "sale_ok": True,
            }
        )
        partner = cls.env["res.partner"].create(
            {
                "name": "Partner Picking Test",
            }
        )
        cls.picking = cls.env["stock.picking"].create(
            {
                "name": "Picking 1",
                "partner_id": partner.id,
                "picking_type_id": cls.env.ref("stock.picking_type_out").id,
                "location_id": loc_stock.id,
                "location_dest_id": loc_customer.id,
                "move_ids": [
                    Command.create(
                        {
                            "name": "test move p1",
                            "product_id": product_1.id,
                            "product_uom_qty": 5,
                            "location_id": loc_stock.id,
                            "location_dest_id": loc_customer.id,
                        },
                    )
                ],
            }
        )
        cls.picking.action_confirm()

    def test_stock_picking_cancel_permission(self):
        """
        Data: 1 confirmed picking.

        case: - cancel the picking
              - add the picking cancel permission group to user and cancel picking
        result: - raise a UserError and the picking is still confirmed
                - succeed and the picking is canceled
        """
        self.assertEqual(self.picking.state, "confirmed")
        error_msg = "You are not allowed to cancel such operation"
        with self.assertRaises(UserError, msg=error_msg):
            self.picking.action_cancel()
        self.assertEqual(self.picking.state, "confirmed")
        # add picking cancel permission group to current user
        self.env.user.groups_id += self.picking_cancel_group
        self.picking.action_cancel()
        self.assertEqual(self.picking.state, "cancel")

    def test_stock_picking_printed_cancel_move(self):
        """
        Data: 1 confirmed picking with 1 move.

        case: - set printed of the picking and cancel the move
              - unset printed of the picking and cancel the move
        result: - raise a UserError and the move is still confirmed
                - succeed and the move is canceled
        """
        # set picking printed to True
        self.picking.printed = True
        move = self.picking.move_ids[0]
        self.assertEqual(move.state, "confirmed")
        error_msg = "You cannot cancel a move that is part of a started picking"
        with self.assertRaises(UserError, msg=error_msg):
            move._action_cancel()
        self.assertEqual(move.state, "confirmed")
        # set picking printed to False
        self.picking.printed = False
        move._action_cancel()
        self.assertEqual(move.state, "cancel")
