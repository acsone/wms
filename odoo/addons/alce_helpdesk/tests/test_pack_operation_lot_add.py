# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestPackOperationLotAdd(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestPackOperationLotAdd, cls).setUpClass()
        cls.category_model = cls.env["product.category"]
        cls.product_model = cls.env["product.product"]
        cls.partner_model = cls.env["res.partner"]

        # force parent_left/right computation
        cls.location_model = cls.env["stock.location"]
        # self.location_model.pool._init = False

        cls.stock_picking_model = cls.env["stock.picking"]
        cls.stock_reception_wizard = cls.env["stock.pack.operation.lot.add"]

        cls.products = [
            cls.product_model.create(d)
            for d in [
                {
                    "name": "Unittest Reception P1",
                    "uom_id": cls.env.ref("product.product_uom_unit").id,
                    "tracking": "lot",
                },
                {
                    "name": "Unittest Reception P2",
                    "uom_id": cls.env.ref("product.product_uom_unit").id,
                    "tracking": "lot",
                },
            ]
        ]

        cls.supplier = cls.partner_model.create(
            {"name": "Unittest supplier", "ref": "839737475756467"}
        )

        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")

        cls.reception_location = cls.location_model.create(
            {
                "name": "reception",
                "location_id": cls.stock_location.id,
                "usage": "internal",
                "act_as_view": True,
            }
        )
        cls.bin1 = cls.location_model.create(
            {
                "name": "bin1",
                "location_id": cls.reception_location.id,
                "usage": "internal",
            }
        )
        cls.bin2 = cls.location_model.create(
            {
                "name": "bin2",
                "location_id": cls.reception_location.id,
                "usage": "internal",
            }
        )
        picking = cls.stock_picking_model.create(
            {
                "picking_type_id": cls.env.ref("stock.picking_type_in").id,
                "location_id": cls.supplier_location.id,
                "location_dest_id": cls.reception_location.id,
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": "move 1",
                            "product_id": product.id,
                            "product_uom_qty": 5,
                            "product_uom": product.uom_id.id,
                            "location_id": cls.supplier_location.id,
                            "location_dest_id": cls.reception_location.id,
                        },
                    )
                    for product in cls.products
                ],
            }
        )
        picking = picking.with_context(test_mode=1)
        picking.action_assign()
        cls.picking = picking
        cls.HelpdeskTicket = cls.env["helpdesk.ticket"]

    def test_receive_surplus_quantities_create_ticket(self):
        picking = self.picking
        # launch wizard
        wiz = self.stock_reception_wizard.with_context(
            default_life_date_allowed=True
        ).new({"picking_id": picking.id})

        op1 = picking.pack_operation_product_ids[0]

        # Simulate putaway to bin1 and bin2
        op1.location_dest_id = self.bin1
        tickets = self.HelpdeskTicket.search([])
        # receive surplus
        wiz.operation_id = op1
        wiz._onchange_operation_id()
        self.assertEqual(wiz.remaining_qty, 5)
        wiz.qty = 10
        wiz.is_surplus_qty_confirmed = True
        wiz.button_nextop()
        self.assertEqual(op1.qty_done, 10)

        # check created ticket
        new_tickets = self.HelpdeskTicket.search([]) - tickets
        self.assertTrue(new_tickets)
        self.assertTrue(
            new_tickets.helpdesk_ticket_reason_id,
            self.env.ref("alce_helpdesk.higher_quantity"),
        )
