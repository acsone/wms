# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.fields import Command
from odoo.tests.common import TransactionCase


class TestPermissionPrinterSelection(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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

        cls.printer2 = Printer.create(
            {
                "name": "Test printer 2",
                "system_name": "test_printer_2",
                "server_id": printer_server.id,
            }
        )

        cls.ChangePrinterWizard = cls.env["select.printing.printer"]

    def test_00_can_change_the_printer(self):
        self.env.user.write(
            {
                "groups_id": [
                    Command.link(
                        self.ref(
                            "alc_label_printing_reception.reception_change_printer"
                        ),
                    )
                ],
            }
        )
        self.assertTrue(
            self.env.user.has_group(
                "alc_label_printing_reception.reception_change_printer"
            )
        )
        self.assertFalse(self.env.user.printing_product_label_printer_id)

        wiz = self.ChangePrinterWizard.create({"printer_id": self.printer1.id})
        wiz.change_printer()
        self.assertEqual(self.env.user.printing_product_label_printer_id, self.printer1)

        wiz.write({"printer_id": self.printer2.id})
        wiz.change_printer()
        self.assertEqual(self.env.user.printing_product_label_printer_id, self.printer2)

    def test_01_cannot_change_the_printer(self):
        self.assertFalse(
            self.env.user.has_group(
                "alc_label_printing_reception.reception_change_printer"
            )
        )
        self.assertFalse(self.env.user.printing_product_label_printer_id)
        wiz = self.ChangePrinterWizard.create({"printer_id": self.printer1.id})

        with self.assertRaises(UserError):
            wiz.change_printer()
