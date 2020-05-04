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
        cls.ticket_reason = cls.helpdesk_ticket_reason_model.create(
            {"name": "Unittest helpdesk ticket reason"}
        )

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
                "is_sale_back_order_accepted": True,
                "is_purchase_back_order_accepted": True,
                "ref": "123321",
            }
        )

        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.output_location = cls.env.ref("stock.stock_location_output")
        cls.grn = cls.env["stock.grn"].create({"carrier_id": cls.partner.id})

        ##################
        # incoming picking
        ##################
        picking_type_in_id = cls.env.ref("stock.picking_type_in").id
        location_id = cls.supplier_location.id
        location_dest_id = cls.stock_location.id
        # Create picking
        cls.picking_in = cls.stock_picking_model.create(
            {
                "picking_type_id": picking_type_in_id,
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
        # Transfer picking partially
        cls.picking_in.action_confirm()
        cls.picking_in.force_assign()
        pack_operation = cls.picking_in.pack_operation_product_ids
        pack_operation.write({"qty_done": 3})

        ##################
        # outgoing picking
        ##################
        picking_type_out_id = cls.env.ref("stock.picking_type_out").id
        location_id = cls.stock_location.id
        location_dest_id = cls.supplier_location.id
        # Create picking
        cls.picking_out = cls.stock_picking_model.create(
            {
                "picking_type_id": picking_type_out_id,
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
        # Transfer picking partially
        cls.picking_out.action_confirm()
        cls.picking_out.force_assign()
        pack_operation = cls.picking_in.pack_operation_product_ids
        pack_operation.write({"qty_done": 3})

    def _get_backorder(self, picking):
        return self.stock_picking_model.search([("backorder_id", "=", picking.id)])

    def _process_and_create_backorder(self, picking):
        result = picking.do_new_transfer()
        if result:
            backorder_reason = self.backorder_reason_model.create(
                {
                    "name": "Unittest backorder",
                    "backorder_action_to_do": "create",
                    "is_helpdesk_ticket_to_create": False,
                    "helpdesk_ticket_reason_id": self.ticket_reason.id,
                }
            )

            result = self.picking_in.do_new_transfer()

            # Check that the transfer action return the good wizard
            self.assertEqual(result["res_model"], "stock.backorder.choice")

            # Create backorder choice wizard and execute it
            wizard = self.backorder_choice_model.with_context(result["context"]).create(
                {
                    "reason_id": backorder_reason.id,
                    "helpdesk_ticket_description": "test",
                }
            )
            wizard.apply()
        return self._get_backorder(picking)

    def test_00(self):
        """
        Data:
            An incoming picking type partially processed (3 of 10 products)
        Test case:
            Create a backorder.
        Expected result:
            A backorder is created 1 pack operation
        """
        backorder = self._process_and_create_backorder(self.picking_in)
        self.assertTrue(backorder)
        self.assertTrue(backorder.pack_operation_product_ids)

    def test_01(self):
        """
        Data:
            An outgoring picking type partially processed (3 of 10 products)
        Test case:
            Create a backorder.
        Expected result:
            A backorder is created 1 pack operation
        """
        backorder = self._process_and_create_backorder(self.picking_out)
        self.assertTrue(backorder)
        self.assertTrue(backorder.pack_operation_product_ids)
