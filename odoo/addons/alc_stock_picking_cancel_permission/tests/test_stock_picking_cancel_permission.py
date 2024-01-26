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
        cls.loc_stock = cls.env.ref("stock.stock_location_stock")
        cls.loc_customer = cls.env.ref("stock.stock_location_customers")
        cls.loc_suppliers = cls.env.ref("stock.stock_location_suppliers")
        cls.product_1 = cls.env["product.product"].create(
            {
                "name": "test product 1",
                "type": "product",
                "sale_ok": True,
            }
        )

        cls.product_2 = cls.env["product.product"].create(
            {
                "name": "test product 2",
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
                "location_id": cls.loc_stock.id,
                "location_dest_id": cls.loc_customer.id,
                "move_ids": [
                    Command.create(
                        {
                            "name": "test move p1",
                            "product_id": cls.product_1.id,
                            "product_uom_qty": 5,
                            "location_id": cls.loc_stock.id,
                            "location_dest_id": cls.loc_customer.id,
                        },
                    ),
                    Command.create(
                        {
                            "name": "test move p2",
                            "product_id": cls.product_2.id,
                            "product_uom_qty": 5,
                            "location_id": cls.loc_stock.id,
                            "location_dest_id": cls.loc_customer.id,
                        },
                    ),
                ],
            }
        )
        cls.picking.action_confirm()

        cls.picking_in = cls.env["stock.picking"].create(
            {
                "name": "Picking IN",
                "partner_id": partner.id,
                "picking_type_id": cls.env.ref("stock.picking_type_in").id,
                "location_id": cls.loc_suppliers.id,
                "location_dest_id": cls.loc_stock.id,
                "move_ids": [
                    Command.create(
                        {
                            "name": "test move p1",
                            "product_id": cls.product_1.id,
                            "product_uom_qty": 5,
                            "location_id": cls.loc_suppliers.id,
                            "location_dest_id": cls.loc_stock.id,
                        },
                    ),
                    Command.create(
                        {
                            "name": "test move p2",
                            "product_id": cls.product_2.id,
                            "product_uom_qty": 5,
                            "location_id": cls.loc_suppliers.id,
                            "location_dest_id": cls.loc_stock.id,
                        },
                    ),
                ],
            }
        )
        cls.picking.action_confirm()

    @classmethod
    def _create_quantities(cls, product):
        cls.env["stock.quant"].create(
            {
                "product_id": product.id,
                "location_id": cls.loc_stock.id,
                "inventory_quantity": 50.0,
            }
        )._apply_inventory()

    def test_stock_picking_cancel_permission(self):
        """
        Data: 1 confirmed picking.

        case: - cancel the picking
              - add the picking cancel permission group to user and cancel picking
        result: - raise a UserError and the picking is still confirmed
                - succeed and the picking is canceled
        """
        self.assertEqual(self.picking.state, "confirmed")
        picking_name = self.picking.name
        error_msg = (
            f"You are not allowed to cancel such operation (Picking: {picking_name})"
        )
        with self.assertRaises(UserError) as raises:
            self.picking.action_cancel()
        self.assertEqual(raises.exception.name, error_msg)
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

    def test_stock_picking_backorder(self):
        """
        Data: 1 confirmed picking with 1 move.

        case: - set printed of the picking
              - Partially transfer the picking
        result: - the backorder should be successfully created
        """
        self._create_quantities(self.product_1)
        self._create_quantities(self.product_2)
        self.picking_in.action_assign()
        self.picking_in.printed = True
        self.picking_in.move_line_ids[0].qty_done = 4.0
        res = self.picking_in.button_validate()
        self.assertEqual(res.get("res_model"), "stock.backorder.confirmation")
        wizard = (
            self.env["stock.backorder.confirmation"]
            .with_context(
                **res.get("context"),
            )
            .create({})
        )
        wizard.process_cancel_backorder()
        self.assertFalse(self.picking_in.backorder_ids)

    def test_stock_picking_backorder_never(self):
        """
        Data: 1 confirmed picking with 1 move.

        case: - set printed of the picking
              - Partially transfer the picking
        result: - the backorder should be successfully created
        """
        # create an in
        self._create_quantities(self.product_1)
        self._create_quantities(self.product_2)
        self.picking.picking_type_id.create_backorder = "never"
        self.picking.action_assign()
        self.picking.printed = True
        self.picking.move_line_ids[0].qty_done = 4.0
        self.picking.button_validate()
        self.assertSetEqual(
            {"done", "cancel"}, set(self.picking.move_ids.mapped("state"))
        )
        self.assertEqual(self.picking.state, "done")
