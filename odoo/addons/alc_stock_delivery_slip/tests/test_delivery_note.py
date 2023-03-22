# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import base64
import uuid
from datetime import datetime

from odoo.fields import Command
from odoo.tests.common import TransactionCase


class TestStockDeliveryNote(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.smallyear = str(datetime.now().year)[2:]
        # Create a sale tax
        cls.tax = cls.env["account.tax"].create(
            {
                "is_vat": True,
                "amount": 6,
                "name": "test_tax",
            }
        )
        # Create a couple of products
        cls.p1 = cls.env["product.product"].create(
            {
                "name": "Unittest P1",
                "default_code": "5173360",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "type": "product",
            }
        )
        cls.p2 = cls.env["product.product"].create(
            {
                "name": "Unittest P2",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "type": "product",
            }
        )
        cls.p3 = cls.env["product.product"].create(
            {
                "name": "Unittest P3",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "type": "product",
            }
        )

        # Add some stock for p1 and p2
        cls.env["stock.quant"]._update_available_quantity(
            cls.p1, cls.env.ref("stock.stock_location_stock"), 100
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.p2, cls.env.ref("stock.stock_location_stock"), 100
        )
        # Create the partner
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

        # Create the customers
        cls.customer_csv_only = cls.partner.copy(
            {"send_pdf_deliveryship": False, "send_csv_deliveryship": True}
        )

        cls.customer_pdf_only = cls.partner.copy(
            {"send_pdf_deliveryship": True, "send_csv_deliveryship": False}
        )

        cls.customer_pdf_csv = cls.partner.copy(
            {"send_pdf_deliveryship": True, "send_csv_deliveryship": True}
        )

        # Create customer to test that the associate veterinary will not receive
        # the csv/pdf for the customer purchase
        cls.b2c_customer = cls.partner.copy(
            {
                "name": "B2C Customer",
                "email": "new_customer@pytest.com",
            }
        )

        cls.so_csv, cls.picking_csv = cls._create_and_transfer_picking(
            partner=cls.partner, customer=cls.customer_csv_only, lot_name="20170102"
        )

        cls.b2c_so_csv, cls.b2c_picking_csv = cls._create_and_transfer_picking(
            partner=cls.partner, customer=cls.b2c_customer, lot_name="20200102"
        )

        cls.so_pdf, cls.picking_pdf = cls._create_and_transfer_picking(
            partner=cls.partner, customer=cls.customer_pdf_only
        )
        cls.so_pdf_csv, cls.picking_pdf_csv = cls._create_and_transfer_picking(
            partner=cls.partner, customer=cls.customer_pdf_csv
        )

    @classmethod
    def _create_and_transfer_picking(
        cls, partner, product=None, customer=None, lot_name=None
    ):
        lot_name = lot_name or str(uuid.uuid1())
        if product is None:
            product = cls.p1
        so = cls.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "suite_name": "123454321",
                "client_order_ref": "customer.ref.123",
                "order_line": [
                    Command.create(
                        {
                            "name": product.name,
                            "product_id": product.id,
                            "product_uom": cls.env.ref("uom.product_uom_unit").id,
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

        lot = cls.env["stock.lot"].create(
            {
                "expiration_date": "2017-01-31 10:00:00",
                "name": lot_name,
                "product_qty": 10,
                "product_id": product.id,
                "company_id": cls.env.user.company_id.id,
            },
        )
        lines = picking.move_line_ids
        lines.write({"lot_id": lot.id, "qty_done": 10})
        # use context to avoid wizards
        picking.with_context(skip_sms=True, skip_expired=True).button_validate()
        return so, picking

    def test_delivery_note_filename(self):
        """Check the correct generation of the filename."""
        sz_date_done = self.picking_csv.date_done.strftime("%Y-%m-%d %H:%M:%S")
        picking_number = self.picking_csv.name.split("/")[-1]
        expected_filename = (
            "_".join(
                [
                    "NE",
                    "123456789",
                    picking_number,
                    "".join(sz_date_done[:10].split("-")),
                    "".join(sz_date_done[-8:].split(":")),
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
        """Check that the csv document is in the store for customer configured.

        to receive only csv.
        """
        attachments = self.env["ir.attachment"].search(
            [("res_id", "=", self.picking_csv.id)]
        )
        self.assertEqual(len(attachments), 1)
        self.assertTrue(attachments.name.endswith(".csv"))

    def test_creation_note_on_validate_picking_pdf(self):
        """Check that the pdf document is in the store for customer confiured.

        to recieve only pdf.
        """
        attachments = self.env["ir.attachment"].search(
            [("res_id", "=", self.picking_pdf.id)]
        )
        self.assertEqual(len(attachments), 1)
        self.assertTrue(attachments.name.endswith(".pdf"))

    def test_creation_note_on_validate_picking_pdf_csv(self):
        """Check that the pdf and csv documents are in the store for customer.

        confiured to receive csv and pdf format.
        """
        attachments = self.env["ir.attachment"].search(
            [("res_id", "=", self.picking_pdf_csv.id)]
        )
        self.assertEqual(len(attachments), 2)
        extensions = {a.name.split(".")[1] for a in attachments}
        self.assertSetEqual({"csv", "pdf"}, extensions)

    def test_delivery_note_for_vet_with_depo(self):
        """Check the format of the csv with a vet customer."""
        self.partner.vet_depot_number = "778899"
        tax_amount = ",".join(str(self.tax.amount).split("."))
        expected = [
            [self.picking_csv.id, "tester@pytest.com", ""],
            [
                "Prof. HOENS OLIVIER",
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
                        self.partner.vet_depot_number,
                        self.so_csv.suite_name,
                    ]
                ),
                datetime.strftime(datetime.today().date(), "%d-%m-%Y"),
                "",
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
                "Prof. HOENS OLIVIER",
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
                datetime.strftime(datetime.today().date(), "%d-%m-%Y"),
                "",
                "",
            ],
        ]
        lines = self.picking_csv._generate_delivery_note()
        self.assertEqual(lines, expected)

    def test_delivery_note_line_without_vat_tax(self):
        """Check with no vat so vat amount is zero."""
        self.tax.is_vat = False
        expected = [
            [self.picking_csv.id, "tester@pytest.com", ""],
            [
                "Prof. HOENS OLIVIER",
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
                datetime.strftime(datetime.today().date(), "%d-%m-%Y"),
                "",
                "",
            ],
        ]
        lines = self.picking_csv._generate_delivery_note()
        self.assertEqual(lines, expected)

    def test_each_line_finishes_with_separator(self):
        attachments = self.env["ir.attachment"].search(
            [("res_id", "=", self.picking_csv.id)]
        )
        # pylint: disable=deprecated-method
        content = base64.decodebytes(attachments.datas)
        for line in content.splitlines():
            self.assertEqual(line[-1:], b";")
