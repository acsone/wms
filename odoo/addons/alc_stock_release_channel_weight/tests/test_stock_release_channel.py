# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests.common import TransactionCase


class TestStockReleaseChannel(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.StockReleaseChannel = cls.env["stock.release.channel"]
        cls.ProductProduct = cls.env["product.product"]
        cls.StockPicking = cls.env["stock.picking"]
        cls.StockMove = cls.env["stock.move"]
        cls.StockMoveLine = cls.env["stock.move.line"]
        cls.StockPickingType = cls.env["stock.picking.type"]
        cls.StockLocation = cls.env["stock.location"]
        cls.partner_customer = cls.env["res.partner"].create({"name": "Customer A"})

        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.production_location = cls.stock_location.copy(
            {"name": "Production location"}
        )

        cls.outgoing_type = cls.StockPickingType.create(
            {
                "name": "test outgoing stock picking type",
                "code": "outgoing",
                "sequence_code": "OUT",
            }
        )
        cls.incoming_type = cls.StockPickingType.create(
            {
                "name": "test incoming stock picking type",
                "code": "incoming",
                "sequence_code": "IN",
            }
        )
        cls.internal_type = cls.StockPickingType.create(
            {
                "name": "test internal stock picking type",
                "code": "internal",
                "sequence_code": "INT",
            }
        )

        cls.product_a = cls.ProductProduct.create(
            {"name": "Product A", "weight": 1.0, "type": "product"}
        )
        cls.product_b = cls.ProductProduct.create(
            {"name": "Product B", "weight": 1.0, "type": "product"}
        )
        cls.product_c = cls.ProductProduct.create(
            {"name": "Product C", "weight": 1.0, "type": "product"}
        )
        cls.product_d = cls.ProductProduct.create(
            {"name": "Product D", "weight": 1.0, "type": "product"}
        )
        cls.product_e = cls.ProductProduct.create(
            {"name": "Product E", "weight": 1.0, "type": "product"}
        )

        cls.env["stock.quant"]._update_available_quantity(
            cls.product_a, cls.stock_location, 100
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.product_b, cls.stock_location, 1
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.product_c, cls.stock_location, 1
        )

        cls.release_channel = cls.StockReleaseChannel.create(
            {"name": "Release Channel Test"}
        )

    @classmethod
    def _set_picking_assigned(cls, picking):
        picking.action_confirm()
        picking.action_assign()

    @classmethod
    def _get_fresh_total_weight(cls, release_channel):
        """Return total_weight after invalidating cache and flushing."""
        cls.env.cr.flush()
        release_channel.invalidate_cache(["total_weight"])
        return release_channel.total_weight

    def test_compute_total_weight_released_only(self):
        # --- Draft Outgoing Picking - (Should NOT be counted) ---
        self.picking_outgoing_draft = self.StockPicking.create(
            {
                "picking_type_id": self.outgoing_type.id,
                "move_type": "direct",
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "partner_id": self.partner_customer.id,
                "release_channel_id": self.release_channel.id,
                "move_ids_without_package": [
                    Command.create(
                        {
                            "name": "Outgoing Move A (Done)",
                            "product_id": self.product_a.id,
                            "product_uom_qty": 1,
                            "product_uom": self.product_a.uom_id.id,
                            "location_id": self.stock_location.id,
                            "location_dest_id": self.customer_location.id,
                        }
                    ),
                ],
            }
        )

        self.assertEqual(self.picking_outgoing_draft.state, "draft")
        self.assertEqual(self.picking_outgoing_draft.move_ids[0].state, "draft")

        self.assertEqual(
            self._get_fresh_total_weight(self.release_channel),
            0,
            "Draft out picking moves should not be counted",
        )

        # --- Done Outgoing Picking - (Should NOT be counted) ---
        self.picking_outgoing_done = self.StockPicking.create(
            {
                "picking_type_id": self.outgoing_type.id,
                "move_type": "direct",
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "partner_id": self.partner_customer.id,
                "release_channel_id": self.release_channel.id,
                "move_ids_without_package": [
                    Command.create(
                        {
                            "name": "Outgoing Move A (Done)",
                            "product_id": self.product_a.id,
                            "product_uom_qty": 1,
                            "product_uom": self.product_a.uom_id.id,
                            "location_id": self.stock_location.id,
                            "location_dest_id": self.customer_location.id,
                        }
                    ),
                ],
            }
        )

        self._set_picking_assigned(self.picking_outgoing_done)
        for move_line in self.picking_outgoing_done.move_ids[0].move_line_ids:
            move_line.qty_done = self.picking_outgoing_done.move_ids[0].product_uom_qty
        self.picking_outgoing_done.move_ids[0]._action_done()

        self.assertEqual(self.picking_outgoing_done.state, "done")
        self.assertEqual(self.picking_outgoing_done.move_ids[0].state, "done")

        self.assertEqual(
            self._get_fresh_total_weight(self.release_channel),
            0,
            "Done out picking moves should not be counted",
        )

        # --- Partially available Picking Scenario - (Should BE counted) ---
        self.picking_partially_available = self.StockPicking.create(
            {
                "picking_type_id": self.outgoing_type.id,
                "move_type": "direct",
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "partner_id": self.partner_customer.id,
                "release_channel_id": self.release_channel.id,
                "move_ids_without_package": [
                    Command.create(
                        {
                            "name": "Outgoing Move B (Partially available)",
                            "product_id": self.product_b.id,
                            "product_uom_qty": 5,
                            "product_uom": self.product_b.uom_id.id,
                            "location_id": self.stock_location.id,
                            "location_dest_id": self.customer_location.id,
                        }
                    ),
                ],
            }
        )

        self._set_picking_assigned(self.picking_partially_available)

        self.assertEqual(self.picking_partially_available.state, "assigned")
        self.assertEqual(
            self.picking_partially_available.move_ids[0].state, "partially_available"
        )
        self.assertEqual(
            self._get_fresh_total_weight(self.release_channel),
            5,
            "Partially available outgoing stock moves should be counted",
        )

        # --- Assigned Picking Scenario - (Should BE counted) ---
        self.picking_assigned = self.StockPicking.create(
            {
                "picking_type_id": self.outgoing_type.id,
                "move_type": "direct",
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "partner_id": self.partner_customer.id,
                "release_channel_id": self.release_channel.id,
                "move_ids_without_package": [
                    Command.create(
                        {
                            "name": "Outgoing Move C (Assigned)",
                            "product_id": self.product_c.id,
                            "product_uom_qty": 1,
                            "product_uom": self.product_c.uom_id.id,
                            "location_id": self.stock_location.id,
                            "location_dest_id": self.customer_location.id,
                        }
                    ),
                ],
            }
        )
        self._set_picking_assigned(self.picking_assigned)
        self.assertEqual(self.picking_assigned.state, "assigned")
        self.assertEqual(self.picking_assigned.move_ids[0].state, "assigned")
        self.assertEqual(
            self._get_fresh_total_weight(self.release_channel),
            6,
            "Assigned outgoing stock moves should be counted",
        )

        # --- Confirmed Picking Scenario - (Should BE counted) ---
        self.picking_confirmed = self.StockPicking.create(
            {
                "picking_type_id": self.outgoing_type.id,
                "move_type": "direct",
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "partner_id": self.partner_customer.id,
                "release_channel_id": self.release_channel.id,
                "move_ids_without_package": [
                    Command.create(
                        {
                            "name": "Outgoing Move D (Confirmed)",
                            "product_id": self.product_d.id,
                            "product_uom_qty": 1,
                            "product_uom": self.product_d.uom_id.id,
                            "location_id": self.stock_location.id,
                            "location_dest_id": self.customer_location.id,
                        }
                    ),
                ],
            }
        )

        self._set_picking_assigned(self.picking_confirmed)
        self.assertEqual(self.picking_confirmed.state, "confirmed")
        self.assertEqual(self.picking_confirmed.move_ids[0].state, "confirmed")
        self.assertEqual(
            self._get_fresh_total_weight(self.release_channel),
            7,
            "Confirmed outgoing stock moves should be counted",
        )

        # --- Cancelled Picking Scenario (Should NOT be counted) ---
        self.picking_outgoing_cancel = self.StockPicking.create(
            {
                "picking_type_id": self.outgoing_type.id,
                "move_type": "direct",
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "partner_id": self.partner_customer.id,
                "release_channel_id": self.release_channel.id,
                "move_ids_without_package": [
                    Command.create(
                        {
                            "name": "Outgoing Move E (Cancelled)",
                            "product_id": self.product_e.id,
                            "product_uom_qty": 1,
                            "product_uom": self.product_e.uom_id.id,
                            "location_id": self.stock_location.id,
                            "location_dest_id": self.customer_location.id,
                        }
                    ),
                ],
            }
        )
        self._set_picking_assigned(self.picking_outgoing_cancel)
        self.picking_outgoing_cancel.move_ids[0]._action_cancel()

        self.assertEqual(self.picking_outgoing_cancel.state, "cancel")
        self.assertEqual(self.picking_outgoing_cancel.move_ids[0].state, "cancel")

        self.assertEqual(
            self._get_fresh_total_weight(self.release_channel),
            7,
            "Cancelled stock moves should not be counted",
        )

        # --- Incoming Picking - (Should NOT be counted - wrong type) ---
        self.picking_incoming = self.StockPicking.create(
            {
                "picking_type_id": self.incoming_type.id,
                "move_type": "direct",
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
                "partner_id": self.partner_customer.id,
                "release_channel_id": self.release_channel.id,
                "move_ids_without_package": [
                    Command.create(
                        {
                            "name": "Incoming Move A",
                            "product_id": self.product_a.id,
                            "product_uom_qty": 10,
                            "product_uom": self.product_a.uom_id.id,
                            "location_id": self.supplier_location.id,
                            "location_dest_id": self.stock_location.id,
                        }
                    ),
                ],
            }
        )
        self._set_picking_assigned(self.picking_incoming)

        self.assertEqual(self.picking_incoming.state, "assigned")
        self.assertEqual(self.picking_incoming.move_ids[0].state, "assigned")

        self.assertEqual(
            self._get_fresh_total_weight(self.release_channel),
            7,
            "Incoming picking moves should not be couted",
        )

        # --- Internal Picking - (Should NOT be counted - wrong type) ---
        self.picking_internal = self.StockPicking.create(
            {
                "picking_type_id": self.internal_type.id,
                "move_type": "direct",
                "location_id": self.stock_location.id,
                "location_dest_id": self.production_location.id,
                "release_channel_id": self.release_channel.id,
                "move_ids_without_package": [
                    Command.create(
                        {
                            "name": "Internal Move A",
                            "product_id": self.product_a.id,
                            "product_uom_qty": 10,
                            "product_uom": self.product_a.uom_id.id,
                            "location_id": self.stock_location.id,
                            "location_dest_id": self.production_location.id,
                        }
                    ),
                ],
            }
        )
        self._set_picking_assigned(self.picking_internal)

        self.assertEqual(self.picking_internal.state, "assigned")
        self.assertEqual(self.picking_internal.move_ids[0].state, "assigned")

        self.assertEqual(
            self._get_fresh_total_weight(self.release_channel),
            7,
            "Internal picking moves should not be couted",
        )
