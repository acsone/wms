# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest import mock

from odoo.fields import Command
from odoo.tests.common import TransactionCase


class TestPrintingReception(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, round_autoset=False))
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

        cls.reception_location = cls.env["stock.location"].create(
            {
                "name": "reception",
                "location_id": cls.env.ref("stock.stock_location_stock").id,
                "usage": "internal",
            }
        )

        cls.product1 = cls.env["product.product"].create(
            {
                "name": "Unittest Reception P1",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "tracking": "lot",
                "barcode": "1234567",
            }
        )

        cls.lot = cls.env["stock.lot"].create(
            {
                "product_id": cls.product1.id,
                "name": "Unittest Reception L1",
                "company_id": cls.env.user.company_id.id,
            }
        )
        cls.product2 = cls.env["product.product"].create(
            {
                "name": "Unittest Reception P2",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "tracking": "none",
                "barcode": "2345678",
            }
        )
        cls.products = cls.product1 | cls.product2

        cls.picking = cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.env.ref("stock.picking_type_in").id,
                "location_id": cls.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": cls.reception_location.id,
                "move_ids": [
                    Command.create(
                        {
                            "name": "move 1",
                            "product_id": product.id,
                            "product_uom_qty": 5,
                            "product_uom": product.uom_id.id,
                            "location_id": cls.env.ref(
                                "stock.stock_location_suppliers"
                            ).id,
                            "location_dest_id": cls.reception_location.id,
                        },
                    )
                    for product in cls.products
                ],
            }
        )
        cls.picking = cls.picking.with_context(test_mode=True)
        cls.picking.action_assign()

        cls.bin1 = cls.env["stock.location"].create(
            {
                "name": "bin1",
                "location_id": cls.reception_location.id,
                "usage": "internal",
            }
        )
        cls.reception_wizard = cls.env["stock.pack.operation.lot.add"]

        cls.env.user.printing_product_label_printer_id = cls.printer1

    def test_call_printer_from_reception_wizard_lot(self):
        op1 = self.picking.move_line_ids.search([("product_id", "=", self.product1.id)])
        wiz = self.reception_wizard.create(
            {"picking_id": self.picking.id, "qty": 5, "location_dest_id": self.bin1.id}
        )
        wiz.move_line_id = op1.id
        self.assertTrue(wiz.lot_required)
        wiz.lot_name = "Unittest Reception L1"
        wiz.print_qty = 5
        with mock.patch.object(
            self.env["stock.lot"].__class__, "print_lot_label"
        ) as patched_print:
            wiz.print_label()
            self.assertEqual(patched_print.call_count, 1)
            self.assertEqual(patched_print.call_args.args[0], wiz.print_qty)
            self.assertEqual(
                patched_print.call_args.kwargs["printer_id"], self.printer1.id
            )

    def test_call_printer_from_reception_wizard_product(self):
        op2 = self.picking.move_line_ids.search([("product_id", "=", self.product2.id)])
        wiz = self.reception_wizard.create(
            {"picking_id": self.picking.id, "qty": 5, "location_dest_id": self.bin1.id}
        )
        wiz.move_line_id = op2.id
        self.assertFalse(wiz.lot_required)
        wiz.print_qty = 5
        with mock.patch.object(
            self.env["product.product"].__class__, "print_product_label"
        ) as patched_print:
            wiz.print_label()
            self.assertEqual(patched_print.call_count, 1)
            self.assertEqual(patched_print.call_args[0][0], wiz.print_qty)
            self.assertEqual(patched_print.call_args[1]["printer_id"], self.printer1.id)
