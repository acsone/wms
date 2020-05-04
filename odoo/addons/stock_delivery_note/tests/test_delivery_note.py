# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from datetime import datetime

from odoo.tests.common import SavepointCase


class TestStockDeliveryNote(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestStockDeliveryNote, cls).setUpClass()

        cls.smallyear = str(datetime.now().year)[2:]
        # Create a sale tax
        cls.tax = cls.env["account.tax"].create(
            {
                "tax_group_id": cls.env.ref("specific_data.vat_tax_group").id,
                "amount": 6,
                "name": "test_tax",
            }
        )
        # Create a couple of products
        cls.p1 = cls.env["product.product"].create(
            {
                "name": "Unittest P1",
                "default_code": "5173360",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "consu",
            }
        )
        cls.p2 = cls.env["product.product"].create(
            {
                "name": "Unittest P2",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
            }
        )
        cls.p3 = cls.env["product.product"].create(
            {
                "name": "Unittest P3",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
            }
        )
        # Add some stock for p1 and p2
        inventory = cls.env["stock.inventory"].create(
            {
                "name": "Test",
                "location_id": cls.env.ref("stock.stock_location_stock").id,
                "filter": "partial",
            }
        )
        inventory.prepare_inventory()
        cls.env["stock.inventory.line"].create(
            {
                "inventory_id": inventory.id,
                "product_id": cls.p1.id,
                "product_uom_id": cls.env.ref("product.product_uom_unit").id,
                "product_qty": 100,
                "location_id": cls.env.ref("stock.stock_location_stock").id,
            }
        )
        inventory.action_done()
        inventory = cls.env["stock.inventory"].create(
            {
                "name": "Test",
                "location_id": cls.env.ref("stock.stock_location_stock").id,
                "filter": "partial",
            }
        )
        inventory.prepare_inventory()
        cls.env["stock.inventory.line"].create(
            {
                "inventory_id": inventory.id,
                "product_id": cls.p2.id,
                "product_uom_id": cls.env.ref("product.product_uom_unit").id,
                "product_qty": 100,
                "location_id": cls.env.ref("stock.stock_location_stock").id,
            }
        )
        inventory.action_done()
        # Create the customer
        cls.partner = cls.env["res.partner"].create(
            {
                "title": cls.env.ref("base.res_partner_title_prof").id,
                "name": "HOENS OLIVIER",
                "email": "tester@pytest.com",
                "ref": "123456789",
                "street": "Rue Polisart 2 A",
                "zip": "5300",
                "city": "ANDENNE",
                "country_id": cls.env.ref("base.be").id,
            }
        )
        cls.destination = cls.env.ref("stock.stock_location_customers")
        cls.so = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "suite_name": "123454321",
                "client_order_ref": "customer.ref.123",
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": cls.p1.name,
                            "product_id": cls.p1.id,
                            "product_uom": cls.env.ref("product.product_uom_unit").id,
                            "product_uom_qty": 10,
                            "price_unit": 50,
                            "tax_id": [(4, cls.tax.id, False)],
                        },
                    )
                ],
            }
        )
        cls.so.action_confirm()
        cls.picking = cls.so.picking_ids
        cls.picking.action_assign()
        pack_operation = cls.picking.pack_operation_product_ids
        pack_operation.write(
            {
                "pack_lot_ids": [
                    (
                        0,
                        0,
                        {
                            "life_date": "2017-01-31 10:00:00",
                            "lot_name": "20170102",
                            "qty": 10,
                        },
                    )
                ],
                "qty_done": 10,
            }
        )

    def setUp(self):
        super(TestStockDeliveryNote, self).setUp()
        # do new transfer must be done in setUp as
        # setUpClass doesn't set odoo.tools.config['test_enable']
        self.picking.do_transfer()
        # This is a hack because the reserved_quant_id are not filled up
        # And they are needed by the get_lot in stock.move
        for sm in self.picking.move_lines:
            sm.linked_move_operation_ids[0].reserved_quant_id = sm.quant_ids[0]

    def test_delivery_note_filename(self):
        """Check the correct generation of the filename"""
        expected_filename = (
            "_".join(
                [
                    "NE",
                    "123456789",
                    str(self.picking.id),
                    "".join(self.picking.date_done[:10].split("-")),
                    "".join(self.picking.date_done[-8:].split(":")),
                ]
            )
            + ".csv"
        )
        filename = self.picking._get_delivery_note_filename()
        self.assertEqual(filename, expected_filename)

    def test_creation_note_on_validate_picking(self):
        """Check that the csv document is in the store."""
        attachments = self.env["ir.attachment"].search(
            [("res_id", "=", self.picking.id)]
        )
        self.assertEqual(len(attachments), 1)

    def test_delivery_note_for_vet_with_depo(self):
        """Check the format of the csv with a vet customer."""
        self.partner.vet_depot_number = "778899"
        tax_amount = ",".join(str(self.tax.amount).split("."))
        expected = [
            [self.picking.id, "tester@pytest.com", ""],
            [
                u"Prof. HOENS OLIVIER",
                "Rue Polisart 2 A",
                "5300 ANDENNE",
                self.env.ref("base.be").name,
                "",
            ],
            [
                "5173360",
                self.p1.name,
                "10,000",
                "50,00",
                "50,00",
                tax_amount,
                "20170102",
                "31-01-2017",
                "/".join(
                    [self.smallyear, self.partner.vet_depot_number, self.so.suite_name]
                ),
                "",
            ],
        ]
        lines = self.picking._generate_delivery_note()
        self.assertEqual(lines, expected)

    def test_delivery_note_line_for_other_customer(self):
        """Check the format of the csv document for a normal customer."""
        tax_amount = ",".join(str(self.tax.amount).split("."))
        expected = [
            [self.picking.id, "tester@pytest.com", ""],
            [
                u"Prof. HOENS OLIVIER",
                "Rue Polisart 2 A",
                "5300 ANDENNE",
                self.env.ref("base.be").name,
                "",
            ],
            [
                "5173360",
                self.p1.name,
                "10,000",
                "50,00",
                "50,00",
                tax_amount,
                "20170102",
                "31-01-2017",
                "customer.ref.123",
                "",
            ],
        ]
        lines = self.picking._generate_delivery_note()
        self.assertEqual(lines, expected)

    def test_delivery_note_line_without_vat_tax(self):
        """Check with no vat so vat amount is zero"""
        self.tax.tax_group_id = self.env.ref("account.tax_group_taxes").id
        expected = [
            [self.picking.id, "tester@pytest.com", ""],
            [
                u"Prof. HOENS OLIVIER",
                "Rue Polisart 2 A",
                "5300 ANDENNE",
                self.env.ref("base.be").name,
                "",
            ],
            [
                "5173360",
                self.p1.name,
                "10,000",
                "50,00",
                "50,00",
                "0,0",
                "20170102",
                "31-01-2017",
                "customer.ref.123",
                "",
            ],
        ]
        lines = self.picking._generate_delivery_note()
        self.assertEqual(lines, expected)

    def test_each_line_finishes_with_separator(self):
        """"""
        attachments = self.env["ir.attachment"].search(
            [("res_id", "=", self.picking.id)]
        )
        content = attachments.index_content
        for line in content.splitlines():
            self.assertEqual(line[-1:], ";")
