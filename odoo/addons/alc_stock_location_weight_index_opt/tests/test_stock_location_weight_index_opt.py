# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestLocationWeightIndexOpt(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {
                "name": "Weighted Product",
                "type": "product",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "weight": 2.0,
            }
        )

        cls.location_internal = cls.env["stock.location"].create(
            {
                "name": "Internal Location",
                "usage": "internal",
            }
        )

        cls.location_customer = cls.env["stock.location"].create(
            {
                "name": "Customer Location",
                "usage": "customer",
            }
        )

        cls.picking = cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.env.ref("stock.picking_type_out").id,
                "location_id": cls.location_internal.id,
                "location_dest_id": cls.location_customer.id,
            }
        )

        # Outgoing move: internal → customer
        cls.move_out = cls.env["stock.move"].create(
            {
                "name": "Move Out",
                "product_id": cls.product.id,
                "product_uom_qty": 1.0,
                "product_uom": cls.product.uom_id.id,
                "location_id": cls.location_internal.id,
                "location_dest_id": cls.location_customer.id,
                "picking_id": cls.picking.id,
                "state": "assigned",
            }
        )

        cls.move_out_line = cls.env["stock.move.line"].create(
            {
                "move_id": cls.move_out.id,
                "product_id": cls.product.id,
                "product_uom_id": cls.product.uom_id.id,
                "qty_done": 1.0,
                "location_id": cls.location_internal.id,
                "location_dest_id": cls.location_customer.id,
                "picking_id": cls.picking.id,
            }
        )

        # Incoming move: customer → internal
        cls.move_in = cls.env["stock.move"].create(
            {
                "name": "Move In",
                "product_id": cls.product.id,
                "product_uom_qty": 1.0,
                "product_uom": cls.product.uom_id.id,
                "location_id": cls.location_customer.id,
                "location_dest_id": cls.location_internal.id,
                "state": "assigned",
            }
        )

        cls.move_in_line = cls.env["stock.move.line"].create(
            {
                "move_id": cls.move_in.id,
                "product_id": cls.product.id,
                "product_uom_id": cls.product.uom_id.id,
                "qty_done": 1.0,
                "location_id": cls.location_customer.id,
                "location_dest_id": cls.location_internal.id,
            }
        )

    def test_compute_move_line_ids(self):
        """Test computed incoming and outgoing move lines on internal location."""
        self.assertIn(
            self.move_in_line,
            self.location_internal.incoming_move_line_ids,
            "Expected move_in_line in incoming_move_line_ids",
        )
        self.assertIn(
            self.move_out_line.id,
            self.location_internal.outgoing_move_line_ids.ids,
            "Expected move_out_line in outgoing_move_line_ids",
        )

    def test_search_incoming_move_line_ids(self):
        locations = self.env["stock.location"].search(
            [("incoming_move_line_ids", "in", self.move_in_line.ids)]
        )
        self.assertIn(
            self.location_internal,
            locations,
            "Search should return location for incoming move line",
        )

    def test_search_outgoing_move_line_ids(self):
        locations = self.env["stock.location"].search(
            [("outgoing_move_line_ids", "in", self.move_out_line.ids)]
        )
        self.assertIn(
            self.location_internal,
            locations,
            "Search should return location for outgoing move line",
        )

    def test_non_internal_location_has_no_move_lines(self):
        self.assertFalse(self.location_customer.incoming_move_line_ids)
        self.assertFalse(self.location_customer.outgoing_move_line_ids)

    def test_search_outgoing_move_line_with_move_id(self):
        locations = self.env["stock.location"].search(
            [("outgoing_move_line_ids.move_id", "=", self.move_out.id)]
        )
        self.assertIn(self.location_internal, locations)

    def test_search_incoming_move_line_with_move_id(self):
        locations = self.env["stock.location"].search(
            [("incoming_move_line_ids.move_id", "=", self.move_in.id)]
        )
        self.assertIn(self.location_internal, locations)

    def test_search_outgoing_move_line_is_set(self):
        locations = self.env["stock.location"].search(
            [("outgoing_move_line_ids", "=", True)]
        )
        self.assertIn(self.location_internal, locations)
        self.assertNotIn(self.location_customer, locations)

    def test_search_outgoing_move_line_is_not_set(self):
        locations = self.env["stock.location"].search(
            [("outgoing_move_line_ids", "=", False)]
        )
        self.assertIn(self.location_customer, locations)
        self.assertNotIn(self.location_internal, locations)

    def test_weight_before_and_after_internal_picking_done(self):
        internal_1 = self.location_internal
        internal_2 = self.env["stock.location"].create(
            {"name": "Internal 2", "usage": "internal"}
        )

        picking_type = self.env.ref("stock.picking_type_internal")

        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": picking_type.id,
                "location_id": internal_1.id,
                "location_dest_id": internal_2.id,
            }
        )

        self.env["stock.move"].create(
            {
                "name": "Internal Move",
                "product_id": self.product.id,
                "product_uom_qty": 3.0,
                "product_uom": self.product.uom_id.id,
                "location_id": internal_1.id,
                "location_dest_id": internal_2.id,
                "picking_id": picking.id,
            }
        )

        self.assertEqual(internal_1.net_weight, 0.0)
        self.assertEqual(internal_2.net_weight, 0.0)

        self.env["stock.quant"]._update_available_quantity(
            self.product, internal_1, 3.0
        )
        picking.action_confirm()
        picking.action_assign()

        self.assertEqual(internal_1.net_weight, 6.0)
        self.assertEqual(internal_2.net_weight, 0.0)

        picking.action_set_quantities_to_reservation()
        picking.button_validate()

        self.assertEqual(
            internal_1.net_weight,
            0.0,
            "Source location should have 0 weight after picking",
        )
        self.assertEqual(
            internal_2.net_weight,
            6.0,
            "Dest location should have total weight (3 * 2.0)",
        )
