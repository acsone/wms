# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestProductExpiry(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.warehouse.delivery_steps = "pick_ship"
        cls.loc_stock = cls.warehouse.lot_stock_id
        cls.warehouse.route_ids.available_to_promise_defer_pull = True
        cls.product = cls.env["product.product"].create(
            {
                "name": "product",
                "tracking": "lot",
                "type": "product",
                "use_expiration_date": True,
            }
        )
        cls.expired_lot = cls.env["stock.lot"].create(
            {
                "name": "lot",
                "product_id": cls.product.id,
                "expiration_date": "2023-01-31",
            }
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.product, cls.loc_stock, 3, lot_id=cls.expired_lot
        )
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.picking_customer = cls.env["stock.picking"].create(
            {
                "location_id": cls.warehouse.wh_output_stock_loc_id.id,
                "location_dest_id": cls.customer_location.id,
                "picking_type_id": cls.warehouse.out_type_id.id,
                "move_ids": [
                    Command.create(
                        {
                            "name": cls.product.name,
                            "product_id": cls.product.id,
                            "product_uom_qty": 3,
                            "location_id": cls.warehouse.wh_output_stock_loc_id.id,
                            "location_dest_id": cls.customer_location.id,
                            "procure_method": "make_to_order",
                        }
                    )
                ],
            }
        )
        cls.picking_customer.action_confirm()
        cls.move = cls.picking_customer.move_ids
        cls.pick_type = cls.warehouse.pick_type_id
        cls.out_type = cls.warehouse.out_type_id
        cls.pick_type.no_expired_reservation_allowed = True
        cls.out_type.no_expired_reservation_allowed = True

    @classmethod
    def _do_transfer(cls, pick):
        pick.action_set_quantities_to_reservation()
        pick._action_done()

    def test_0(self):
        """If expired lot allowed, no restriction."""
        self.pick_type.no_expired_reservation_allowed = False
        self.out_type.no_expired_reservation_allowed = False
        self.assertEqual(self.picking_customer.state, "waiting")
        self.assertEqual(self.move.ordered_available_to_promise_qty, 3)
        self.assertTrue(self.move.release_ready)
        self.picking_customer.release_available_to_promise()
        pick = self.move.move_orig_ids.picking_id
        self.assertEqual(pick.state, "assigned")
        self.assertEqual(pick.move_line_ids.lot_id, self.expired_lot)
        self._do_transfer(pick)
        self.assertEqual(pick.state, "done")
        self.assertEqual(self.picking_customer.state, "assigned")
        self._do_transfer(self.picking_customer)
        self.assertEqual(self.picking_customer.state, "done")

    def test_1(self):
        """If expired lot not allowed, lot is processed if removal date is later then scheduled date."""
        self.assertEqual(self.picking_customer.state, "waiting")
        self.assertEqual(self.move.ordered_available_to_promise_qty, 3)
        self.assertTrue(self.move.release_ready)
        self.picking_customer.release_available_to_promise()
        pick = self.move.move_orig_ids.picking_id
        self.assertEqual(pick.state, "confirmed")
        self.assertFalse(pick.move_line_ids)
        pick.scheduled_date = "2023-01-15"
        pick.action_assign()
        self.assertEqual(pick.state, "assigned")
        self.assertEqual(pick.move_line_ids.lot_id, self.expired_lot)
        self._do_transfer(pick)
        self.assertEqual(pick.state, "done")
        self.assertEqual(self.picking_customer.state, "waiting")
        self.picking_customer.scheduled_date = "2023-01-15"
        self.picking_customer.action_assign()
        self.assertEqual(self.picking_customer.state, "assigned")
        self._do_transfer(self.picking_customer)
        self.assertEqual(self.picking_customer.state, "done")

    def test_2(self):
        """If expired lot not allowed, lot is processed if user explictly allow it in pick type."""
        self.assertEqual(self.picking_customer.state, "waiting")
        self.assertEqual(self.move.ordered_available_to_promise_qty, 3)
        self.assertTrue(self.move.release_ready)
        self.picking_customer.release_available_to_promise()
        pick = self.move.move_orig_ids.picking_id
        self.assertEqual(pick.state, "confirmed")
        self.assertFalse(pick.move_line_ids)
        pick.to_process_quant_expired = True
        pick.action_assign()
        self.assertEqual(pick.state, "assigned")
        self.assertEqual(pick.move_line_ids.lot_id, self.expired_lot)
        self._do_transfer(pick)
        self.assertEqual(pick.state, "done")
        self.assertEqual(self.picking_customer.state, "assigned")
        self._do_transfer(self.picking_customer)
        self.assertEqual(self.picking_customer.state, "done")

    def test_3(self):
        """If expired lot not allowed, lot is processed if user explictly allow it in pick."""
        self.assertEqual(self.picking_customer.state, "waiting")
        self.assertEqual(self.move.ordered_available_to_promise_qty, 3)
        self.assertTrue(self.move.release_ready)
        self.picking_customer.release_available_to_promise()
        pick = self.move.move_orig_ids.picking_id
        self.assertEqual(pick.state, "confirmed")
        self.assertFalse(pick.move_line_ids)
        pick.to_process_quant_expired = True
        self.assertTrue(self.picking_customer.to_process_quant_expired)
        pick.action_assign()
        self.assertEqual(pick.state, "assigned")
        self.assertEqual(pick.move_line_ids.lot_id, self.expired_lot)
        self._do_transfer(pick)
        self.assertEqual(pick.state, "done")
        self.assertEqual(self.picking_customer.state, "assigned")
        self._do_transfer(self.picking_customer)
        self.assertEqual(self.picking_customer.state, "done")

    def test_4(self):
        """Check permission is propagated from out to pick."""
        self.picking_customer.release_available_to_promise()
        pick = self.move.move_orig_ids.picking_id
        self.assertFalse(self.picking_customer.to_process_quant_expired)
        self.assertFalse(pick.to_process_quant_expired)
        self.picking_customer.to_process_quant_expired = True
        self.assertTrue(self.picking_customer.to_process_quant_expired)
        self.assertTrue(pick.to_process_quant_expired)
        self.picking_customer.to_process_quant_expired = False
        self.assertFalse(self.picking_customer.to_process_quant_expired)
        self.assertFalse(pick.to_process_quant_expired)

    def test_5(self):
        """Check permission is propagated from pick to out."""
        self.picking_customer.release_available_to_promise()
        pick = self.move.move_orig_ids.picking_id
        self.assertFalse(self.picking_customer.to_process_quant_expired)
        self.assertFalse(pick.to_process_quant_expired)
        pick.to_process_quant_expired = True
        self.assertTrue(self.picking_customer.to_process_quant_expired)
        self.assertTrue(pick.to_process_quant_expired)
        pick.to_process_quant_expired = False
        self.assertFalse(self.picking_customer.to_process_quant_expired)
        self.assertFalse(pick.to_process_quant_expired)

    def test_6(self):
        """If product don't use expiration date, no restriction."""
        self.product.use_expiration_date = False
        self.assertEqual(self.picking_customer.state, "waiting")
        self.assertEqual(self.move.ordered_available_to_promise_qty, 3)
        self.assertTrue(self.move.release_ready)
        self.picking_customer.release_available_to_promise()
        pick = self.move.move_orig_ids.picking_id
        self.assertEqual(pick.state, "assigned")
        self.assertEqual(pick.move_line_ids.lot_id, self.expired_lot)
        self._do_transfer(pick)
        self.assertEqual(pick.state, "done")
        self.assertEqual(self.picking_customer.state, "assigned")
        self._do_transfer(self.picking_customer)
        self.assertEqual(self.picking_customer.state, "done")

    def test_7(self):
        """If expired lot not allowed, but reservation is done, validation is blocked."""
        self.assertEqual(self.picking_customer.state, "waiting")
        self.assertEqual(self.move.ordered_available_to_promise_qty, 3)
        self.assertTrue(self.move.release_ready)
        self.picking_customer.release_available_to_promise()
        pick = self.move.move_orig_ids.picking_id
        self.assertEqual(pick.state, "confirmed")
        self.assertFalse(pick.move_line_ids)
        pick.to_process_quant_expired = True
        self.assertTrue(self.picking_customer.to_process_quant_expired)
        pick.action_assign()
        self.assertEqual(pick.state, "assigned")
        self.assertEqual(pick.move_line_ids.lot_id, self.expired_lot)
        self.picking_customer.to_process_quant_expired = False
        with self.assertRaises(UserError):
            self._do_transfer(pick)
        self.picking_customer.to_process_quant_expired = True
        self._do_transfer(pick)
        self.assertEqual(pick.state, "done")
        self.assertEqual(self.picking_customer.state, "assigned")
        self._do_transfer(self.picking_customer)
        self.assertEqual(self.picking_customer.state, "done")

    def test_8(self):
        """If expired lot not allowed, but reservation is done, validation is blocked."""
        self.picking_customer.release_available_to_promise()
        pick = self.move.move_orig_ids.picking_id
        self.assertEqual(pick.state, "confirmed")
        self.assertFalse(pick.move_line_ids)
        pick.to_process_quant_expired = True
        pick.action_assign()
        self._do_transfer(pick)
        self.assertEqual(self.picking_customer.state, "assigned")
        self.picking_customer.to_process_quant_expired = False
        self.picking_customer.action_set_quantities_to_reservation()
        res = self.picking_customer.button_validate()
        self.assertEqual(res.get("res_model"), "expiry.picking.confirmation")
        self.assertEqual(self.picking_customer.state, "assigned")
        self.picking_customer.to_process_quant_expired = True
        self.picking_customer.button_validate()
        self.assertEqual(self.picking_customer.state, "done")
