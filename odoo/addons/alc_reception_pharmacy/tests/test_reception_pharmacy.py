# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import mock

from .common import CommonReceptionPharmacyCase


class TestReceptionPharmacy(CommonReceptionPharmacyCase):
    @classmethod
    def setUpClass(cls):
        super(TestReceptionPharmacy, cls).setUpClass()
        cls.wizard = cls.env["receive.pharmacy.products"]
        Printer = cls.env["printing.printer"].sudo()
        Printer.search([]).unlink()
        printer_server = (
            cls.env["printing.server"]
            .sudo()
            .create({"name": "Localhost", "address": "no_printing", "port": "1234"})
        )
        cls.printer1 = Printer.create(
            {
                "name": "Test printer 1",
                "system_name": "test_printer_1",
                "server_id": printer_server.id,
            }
        )
        cls.env.user.printing_pharmacy_reception_printer_id = cls.printer1

    def test_00(self):
        # Create reception pharmcy for the given customer
        # assert that the partner_shipping_id = customer delivery id

        # create the existing pick out
        self._create_and_prepare_so()
        # before pharmacy reception, one item to be delivered
        self.assertEqual(len(self.shipping.move_lines), 1)

        reception = self.ReceptionPharmacy.create({"product_id": self.product.id})
        wiz = self.wizard.create(
            {
                "reception_pharmacy_id": reception.id,
                "customer_id": self.partner.id,
                "bin_id": self.bin.id,
                "product_qty": 1,
            }
        )

        with mock.patch.object(
            self.env["reception.pharmacy.line"].__class__,
            "print_reception_pharmacy_label",
        ) as patched_print:
            wiz.validate_reception()
            self.assertEqual(patched_print.call_count, 1)
        pharmacy_line = self.env["reception.pharmacy.line"].search(
            [("wizard_id", "=", reception.id)]
        )
        self.assertEqual(pharmacy_line.partner_shipping_id.id, self.partner.id)

        pickings = reception.validate()

        # after pharmacy reception, 2 items to be delivered
        self.assertEqual(len(self.shipping.move_lines), 2)
        self.assertTrue(pickings.mapped("delivery_round_id"))

    def test_01(self):
        # Create reception pharmacy for the given customer with an existing picking out
        # Check that the pharmacy line is added to the picking out for the customer

        # create the existing pick out
        self._create_and_prepare_so()
        # before pharmacy reception, one item to be delivered
        self.assertEqual(len(self.shipping.move_lines), 1)

        reception = self.ReceptionPharmacy.create({"product_id": self.product.id})
        wiz = self.wizard.create(
            {
                "reception_pharmacy_id": reception.id,
                "customer_id": self.partner.id,
                "bin_id": self.bin.id,
                "product_qty": 1,
            }
        )

        with mock.patch.object(
            self.env["reception.pharmacy.line"].__class__,
            "print_reception_pharmacy_label",
        ) as patched_print:
            wiz.validate_reception()
            self.assertEqual(patched_print.call_count, 1)

        pickings = reception.validate()
        # after pharmacy reception, 2 items to be delivered
        self.assertEqual(len(self.shipping.move_lines), 2)
        self.assertTrue(pickings.mapped("delivery_round_id"))

    def test_is_delivered_by_alcyon(self):
        """
        A customer is delivered by alcyon if it's linked to an itinerary
        """
        self.assertTrue(self.partner.is_delivered_by_alcyon)
        self.itinerary.unlink()
        self.assertFalse(self.partner.is_delivered_by_alcyon)

    def test_no_round_auto_assign_if_alone(self):
        reception = self.ReceptionPharmacy.create({"product_id": self.product.id})
        wiz = self.wizard.create(
            {
                "reception_pharmacy_id": reception.id,
                "customer_id": self.partner.id,
                "bin_id": self.bin.id,
                "product_qty": 1,
            }
        )

        with mock.patch.object(
            self.env["reception.pharmacy.line"].__class__,
            "print_reception_pharmacy_label",
        ) as patched_print:
            pickings = wiz.validate_reception()
            self.assertEqual(patched_print.call_count, 1)

        pickings = reception.validate()
        self.assertFalse(pickings.mapped("delivery_round_id"))
