# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo.tests.common import SavepointCase


class TestPickingBackorder(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestPickingBackorder, cls).setUpClass()
        cls.product_model = cls.env["product.product"]
        cls.partner_model = cls.env["res.partner"]
        cls.location_model = cls.env["stock.location"]
        cls.stock_picking_model = cls.env["stock.picking"]
        cls.stock_picking_type_model = cls.env["stock.picking.type"]
        cls.backorder_reason_model = cls.env["stock.backorder.reason"]
        cls.backorder_choice_model = cls.env["stock.backorder.choice"]
        cls.backorder_confirmation_model = cls.env["stock.backorder.confirmation"]
        cls.helpdesk_ticket_model = cls.env["helpdesk.ticket"]
        cls.helpdesk_ticket_reason_model = cls.env["helpdesk.ticket.reason"]

        cls.product = cls.product_model.create(
            {
                "name": "Unittest P1",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
            }
        )

        cls.partner = cls.partner_model.create(
            {
                "name": "Unittest supplier",
                "is_sale_back_order_accepted": False,
                "ref": "123321",
            }
        )

        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.output_location = cls.env.ref("stock.stock_location_output")
        cls.grn = cls.env["stock.grn"].create({"carrier_id": cls.partner.id})

        picking_type_id = cls.env.ref("stock.picking_type_in").id
        location_id = cls.supplier_location.id
        location_dest_id = cls.stock_location.id
        # Create picking
        cls.picking = cls.stock_picking_model.create(
            {
                "picking_type_id": picking_type_id,
                "location_id": location_id,
                "location_dest_id": location_dest_id,
                "partner_id": cls.partner.id,
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": "a move",
                            "product_id": cls.product.id,
                            "product_uom_qty": 10,
                            "product_uom": cls.product.uom_id.id,
                            "location_id": location_id,
                            "location_dest_id": location_dest_id,
                        },
                    )
                ],
                "grn_id": cls.grn.id,
            }
        )
        cls.picking_waiting_availability = cls.stock_picking_model.create(
            {
                "picking_type_id": cls.env.ref("stock.picking_type_out").id,
                "location_id": cls.stock_location.id,
                "location_dest_id": cls.output_location.id,
                "partner_id": cls.partner.id,
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": "a move",
                            "product_id": cls.product.id,
                            "product_uom_qty": 10,
                            "product_uom": cls.product.uom_id.id,
                            "location_id": cls.stock_location.id,
                            "location_dest_id": cls.output_location.id,
                        },
                    )
                ],
                "grn_id": cls.grn.id,
            }
        )
        # Transfer picking partially
        cls.picking.action_confirm()
        cls.picking.force_assign()
        # Don't force assign to let the picking into waiting availability state
        cls.picking_waiting_availability.action_confirm()
        pack_operation = cls.picking.pack_operation_product_ids
        pack_operation.write({"qty_done": 3})

        # Define helpdesk ticket values
        cls.ticket_reason = cls.helpdesk_ticket_reason_model.create(
            {"name": "Unittest helpdesk ticket reason"}
        )

    def _check_backorder_behavior(
        self, backorder_accepted, backorder_action, helpdesk_needed
    ):
        # Define the backorder behavior on partner
        self.partner.is_purchase_back_order_accepted = backorder_accepted

        # Define backorder reason
        backorder_reason = self.backorder_reason_model.create(
            {
                "name": "Unittest backorder",
                "backorder_action_to_do": backorder_action,
                "is_helpdesk_ticket_to_create": helpdesk_needed,
                "helpdesk_ticket_reason_id": self.ticket_reason.id,
            }
        )

        result = self.picking.do_new_transfer()

        # Check that the transfer action return the good wizard
        self.assertEqual(result["res_model"], "stock.backorder.choice")

        # Create backorder choice wizard and execute it
        wizard = self.backorder_choice_model.with_context(result["context"]).create(
            {"reason_id": backorder_reason.id, "helpdesk_ticket_description": "test"}
        )
        wizard.apply()

        # Search created backorder
        backorder = self.stock_picking_model.search(
            [("backorder_id", "=", self.picking.id)]
        )

        # Check picking values
        self.assertEqual(len(self.picking.move_lines), 1)
        self.assertEqual(self.picking.move_lines.product_id, self.product)
        self.assertEqual(self.picking.move_lines.product_uom_qty, 3)
        self.assertEqual(self.picking.move_lines.state, "done")
        self.assertEqual(self.picking.state, "done")

        # Check backorder values
        self.assertEqual(len(backorder), 1)
        self.assertEqual(backorder.move_lines.product_uom_qty, 7)
        keep_backorder = backorder_action == "create" or (
            backorder_action == "use_partner_option" and backorder_accepted
        )
        self.assertEqual(backorder.state, "assigned" if keep_backorder else "cancel")

        # Check helpdesk ticket creation
        ticket = self.helpdesk_ticket_model.search(
            [("stock_picking_id", "=", self.picking.id)]
        )
        if helpdesk_needed:
            self.assertEqual(len(ticket), 1)
            self.assertEqual(ticket.partner_id, self.partner)
            self.assertEqual(ticket.description, "test")
            # Check that the name has a reference and not the default value
            self.assertTrue(ticket.name)
            self.assertNotEqual(ticket.name, "/")
            self.assertEqual(ticket.helpdesk_ticket_reason_id, self.ticket_reason)
        else:
            self.assertEqual(len(ticket), 0)

    # Test all cases separately to benefit of SavepointCase
    # backorder_action in ['create', 'cancel', 'use_partner_option']
    # backorder_accepted in [False, True]
    # helpdesk_needed in [False, True]

    def test_purchase_picking_backorder_create_backorder_no_helpdesk_1(self):
        backorder_action = "create"
        backorder_accepted = False
        helpdesk_needed = False

        self._check_backorder_behavior(
            backorder_accepted, backorder_action, helpdesk_needed
        )

    def test_purchase_picking_backorder_create_backorder_no_helpdesk_2(self):
        backorder_action = "create"
        backorder_accepted = False
        helpdesk_needed = True

        self._check_backorder_behavior(
            backorder_accepted, backorder_action, helpdesk_needed
        )

    def test_purchase_picking_backorder_create_backorder_no_helpdesk_3(self):
        backorder_action = "create"
        backorder_accepted = True
        helpdesk_needed = False

        self._check_backorder_behavior(
            backorder_accepted, backorder_action, helpdesk_needed
        )

    def test_purchase_picking_backorder_create_backorder_no_helpdesk_4(self):
        backorder_action = "create"
        backorder_accepted = True
        helpdesk_needed = True
        self._check_backorder_behavior(
            backorder_accepted, backorder_action, helpdesk_needed
        )

    def test_purchase_picking_backorder_create_backorder_no_helpdesk_5(self):
        backorder_action = "cancel"
        backorder_accepted = False
        helpdesk_needed = False
        self._check_backorder_behavior(
            backorder_accepted, backorder_action, helpdesk_needed
        )

    def test_purchase_picking_backorder_create_backorder_no_helpdesk_6(self):
        backorder_action = "cancel"
        backorder_accepted = False
        helpdesk_needed = True

        self._check_backorder_behavior(
            backorder_accepted, backorder_action, helpdesk_needed
        )

    def test_purchase_picking_backorder_create_backorder_no_helpdesk_7(self):
        backorder_action = "cancel"
        backorder_accepted = True
        helpdesk_needed = False

        self._check_backorder_behavior(
            backorder_accepted, backorder_action, helpdesk_needed
        )

    def test_purchase_picking_backorder_create_backorder_no_helpdesk_8(self):
        backorder_action = "cancel"
        backorder_accepted = True
        helpdesk_needed = True
        self._check_backorder_behavior(
            backorder_accepted, backorder_action, helpdesk_needed
        )

    def test_purchase_picking_backorder_create_backorder_no_helpdesk_9(self):
        backorder_action = "use_partner_option"
        backorder_accepted = False
        helpdesk_needed = False

        self._check_backorder_behavior(
            backorder_accepted, backorder_action, helpdesk_needed
        )

    def test_purchase_picking_backorder_create_backorder_no_helpdesk_10(self):
        backorder_action = "use_partner_option"
        backorder_accepted = False
        helpdesk_needed = True

        self._check_backorder_behavior(
            backorder_accepted, backorder_action, helpdesk_needed
        )

    def test_purchase_picking_backorder_create_backorder_no_helpdesk_11(self):
        backorder_action = "use_partner_option"
        backorder_accepted = True
        helpdesk_needed = False

        self._check_backorder_behavior(
            backorder_accepted, backorder_action, helpdesk_needed
        )

    def test_purchase_picking_backorder_create_backorder_no_helpdesk_12(self):
        backorder_action = "use_partner_option"
        backorder_accepted = True
        helpdesk_needed = True
        self._check_backorder_behavior(
            backorder_accepted, backorder_action, helpdesk_needed
        )
