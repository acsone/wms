# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.exceptions import UserError
from odoo.fields import Command

from odoo.addons.base.tests.common import BaseCommon


class TestSaleOrderLineCancel(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "partner"})

        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.warehouse.delivery_steps = "pick_ship"
        cls.warehouse.delivery_route_id.available_to_promise_defer_pull = True
        cls.loc_stock = cls.warehouse.lot_stock_id
        cls.product = cls.env["product.product"].create(
            {"name": "product", "type": "product"}
        )
        cls.env["stock.quant"]._update_available_quantity(cls.product, cls.loc_stock, 5)
        cls.so = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "warehouse_id": cls.warehouse.id,
                "order_line": [
                    Command.create(
                        {
                            "name": cls.product.name,
                            "product_id": cls.product.id,
                            "product_uom_qty": 5,
                            "product_uom": cls.product.uom_id.id,
                            "price_unit": 1,
                        },
                    )
                ],
            }
        )
        cls.so.action_confirm()
        cls.so.action_done()

        cls.out = cls.so.picking_ids.filtered(
            lambda p: p.picking_type_id.code == "outgoing"
        )
        cls.wiz = cls.env["sale.order.line.cancel"].create({})
        cls.sol = cls.so.order_line

    @classmethod
    def _do_transfer(cls, picking):
        picking.action_confirm()
        picking.action_assign()
        for move in picking.move_ids:
            move.quantity_done = move.product_qty
        picking._action_done()

    @classmethod
    def _release(cls):
        cls.out.release_available_to_promise()
        cls.pick = cls.so.picking_ids.filtered(
            lambda p: p.picking_type_id.code == "internal"
        )

    def setUp(self):
        super().setUp()
        self._release()

    def _cancel_remaining_qty(self):
        self.wiz.with_context(
            active_id=self.sol.id, active_model=self.sol._name
        ).cancel_remaining_qty()

    def test_cancel_remaining_qty_started_picking(self):
        """Check printed picking can't be canceled."""
        self.pick.printed = True
        picking_name = self.pick.name
        with self.assertRaises(UserError) as error:
            self._cancel_remaining_qty()
        self.assertEqual(
            f"You cannot cancel a quantity that is part of a started picking ({picking_name})",
            error.exception.name,
        )

    def test_cancel_remaining_qty_done_preparation(self):
        """Check done picking can't be canceled."""
        self._do_transfer(self.pick)
        with self.assertRaises(UserError):
            self._cancel_remaining_qty()

    def test_cancel_remaining_qty_partially_done_preparation(self):
        self.pick.move_line_ids.qty_done = 2
        self.pick._action_done()
        with self.assertRaises(UserError):
            # if the preparation is done but the out is not done yet
            # we don't allow line cancel
            self._cancel_remaining_qty()
        self.pick.printed = False
        with self.assertRaises(UserError):
            # even if the pick was done manually, and not printed
            # we don't allow the cancel
            self._cancel_remaining_qty()
        self.out.move_line_ids.qty_done = 2
        self.out._action_done()
        self.assertEqual(self.sol.qty_delivered, 2)
        self.assertEqual(self.sol.product_qty_remains_to_deliver, 3)
        # no the out is done, we allow the cancel of the remaining qties
        self._cancel_remaining_qty()
        self.assertEqual(self.sol.product_qty_canceled, 3)
        self.assertEqual(self.sol.product_qty_remains_to_deliver, 0)
