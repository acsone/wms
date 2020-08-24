# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import uuid
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
        cls.partner_csv_only = cls.env["res.partner"].create(
            {
                "title": cls.env.ref("base.res_partner_title_prof").id,
                "name": "HOENS OLIVIER",
                "email": "tester@pytest.com",
                "ref": "123456789",
                "street": "Rue Polisart 2 A",
                "zip": "5300",
                "city": "ANDENNE",
                "country_id": cls.env.ref("base.be").id,
                "send_pdf_deliveryship": False,
                "send_csv_deliveryship": True,
            }
        )
        cls.partner_pdf_only = cls.partner_csv_only.copy(
            {"send_pdf_deliveryship": True, "send_csv_deliveryship": False}
        )

        cls.partner_pdf_csv = cls.partner_pdf_only.copy(
            {"send_pdf_deliveryship": True, "send_csv_deliveryship": True}
        )

        # Create b2c customer to test that the associate veterinary will not receive the csv/pdf
        # for the b2c customer purchase
        cls.b2c_customer = cls.partner_csv_only.copy(
            {
                "is_b2c_customer": True,
                "name": "B2C Customer",
                "email": "new_customer@pytest.com",
            }
        )

        cls.so_csv, cls.picking_csv = cls._create_and_transfer_picking(
            cls.partner_csv_only, lot_name="20170102"
        )

        cls.b2c_so_csv, cls.b2c_picking_csv = cls._create_and_transfer_picking(
            partner=cls.partner_csv_only, customer=cls.b2c_customer, lot_name="20200102"
        )

        cls.so_pdf, cls.picking_pdf = cls._create_and_transfer_picking(
            cls.partner_pdf_only
        )
        cls.so_pdf_csv, cls.picking_pdf_csv = cls._create_and_transfer_picking(
            cls.partner_pdf_csv
        )

    @classmethod
    def _create_and_transfer_picking(cls, partner, customer=None, lot_name=None):
        lot_name = lot_name or str(uuid.uuid1())
        so = cls.env["sale.order"].create(
            {
                "partner_id": partner.id,
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
        so.action_confirm()
        picking = so.picking_ids
        if customer:
            picking.customer_id = customer.id
        picking.action_assign()
        pack_operation = picking.pack_operation_product_ids
        pack_operation.write(
            {
                "pack_lot_ids": [
                    (
                        0,
                        0,
                        {
                            "life_date": "2017-01-31 10:00:00",
                            "lot_name": lot_name,
                            "qty": 10,
                        },
                    )
                ],
                "qty_done": 10,
            }
        )

        picking.do_transfer()
        # This is a hack because the reserved_quant_id are not filled up
        # And they are needed by the get_lot in stock.move
        for sm in picking.move_lines:
            sm.linked_move_operation_ids[0].reserved_quant_id = sm.quant_ids[0]
        return so, picking

    def test_delivery_note_filename(self):
        """Check the correct generation of the filename"""
        expected_filename = (
            "_".join(
                [
                    "NE",
                    "123456789",
                    str(self.picking_csv.id),
                    "".join(self.picking_csv.date_done[:10].split("-")),
                    "".join(self.picking_csv.date_done[-8:].split(":")),
                ]
            )
            + ".csv"
        )
        filename = self.picking_csv._get_delivery_note_filename(".csv")
        self.assertEqual(filename, expected_filename)

    def test_email_not_sent_to_partner(self):
        """Use partner mail if recipient customer has an email."""
        values = {"partner_ids": [self.b2c_customer.id]}
        self.assertEqual(
            self.env["stock.picking"]._delivery_note_recipient_ids(values),
            [self.b2c_customer.id],
        )

    def test_creation_note_on_validate_picking_csv(self):
        """Check that the csv document is in the store for partner confiured
        to recieve only csv."""
        attachments = self.env["ir.attachment"].search(
            [("res_id", "=", self.picking_csv.id)]
        )
        self.assertEqual(len(attachments), 1)
        self.assertTrue(attachments.datas_fname.endswith(".csv"))

    def test_creation_note_on_validate_picking_pdf(self):
        """Check that the pdf document is in the store for partner confiured
        to recieve only pdf."""
        attachments = self.env["ir.attachment"].search(
            [("res_id", "=", self.picking_pdf.id)]
        )
        self.assertEqual(len(attachments), 1)
        self.assertTrue(attachments.datas_fname.endswith(".pdf"))

    def test_creation_note_on_validate_picking_pdf_csv(self):
        """Check that the pdf and csv documents are in the store for partner
        confiured to recieve csv and ofmrat."""
        attachments = self.env["ir.attachment"].search(
            [("res_id", "=", self.picking_pdf_csv.id)]
        )
        self.assertEqual(len(attachments), 2)
        extensions = {a.datas_fname.split(".")[1] for a in attachments}
        self.assertSetEqual({"csv", "pdf"}, extensions)

    def test_delivery_note_for_vet_with_depo(self):
        """Check the format of the csv with a vet customer."""
        self.partner_csv_only.vet_depot_number = "778899"
        tax_amount = ",".join(str(self.tax.amount).split("."))
        expected = [
            [self.picking_csv.id, "tester@pytest.com", ""],
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
                    [
                        self.smallyear,
                        self.partner_csv_only.vet_depot_number,
                        self.so_csv.suite_name,
                    ]
                ),
                "",
            ],
        ]
        lines = self.picking_csv._generate_delivery_note()
        self.assertEqual(lines, expected)

    def test_delivery_note_line_for_other_customer(self):
        """Check the format of the csv document for a normal customer."""
        tax_amount = ",".join(str(self.tax.amount).split("."))
        expected = [
            [self.picking_csv.id, "tester@pytest.com", ""],
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
        lines = self.picking_csv._generate_delivery_note()
        self.assertEqual(lines, expected)

    def test_delivery_note_line_without_vat_tax(self):
        """Check with no vat so vat amount is zero"""
        self.tax.tax_group_id = self.env.ref("account.tax_group_taxes").id
        expected = [
            [self.picking_csv.id, "tester@pytest.com", ""],
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
        lines = self.picking_csv._generate_delivery_note()
        self.assertEqual(lines, expected)

    def test_each_line_finishes_with_separator(self):
        """"""
        attachments = self.env["ir.attachment"].search(
            [("res_id", "=", self.picking_csv.id)]
        )
        content = attachments.index_content
        for line in content.splitlines():
            self.assertEqual(line[-1:], ";")
