# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from unittest import mock

from freezegun import freeze_time

from odoo.addons.alc_reception_pharmacy.tests.common import CommonReceptionPharmacyCase


class TestLifeDateOnReceptionPharmacy(CommonReceptionPharmacyCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner.not_in_dynamic_delivery_round = True
        cls.env = cls.env(
            context=dict(
                cls.env.context, test_queue_job_no_delay=True, mail_notrack=True
            )
        )
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

    @freeze_time("2023-01-01 00:00:00")
    def test_00_automatic_life_date(self):
        self.assertTrue(self.partner.is_delivered_by_alcyon)
        reception = self.ReceptionPharmacy.create({"product_id": self.product.id})
        wiz = self.wizard.create(
            {
                "reception_pharmacy_id": reception.id,
                "customer_id": self.partner.id,
                "bin_id": self.bin.id,
                "lot_name": "TC12345",
                "product_qty": 1,
            }
        )

        with mock.patch.object(
            self.env["reception.pharmacy.line"].__class__,
            "print_reception_pharmacy_label",
        ):
            wiz.validate_reception()

        pharmacy_line = self.env["reception.pharmacy.line"].search(
            [("wizard_id", "=", reception.id)]
        )
        lot = pharmacy_line.lot_id

        self.assertEqual(lot.life_date, "2023-01-01 00:00:00")
