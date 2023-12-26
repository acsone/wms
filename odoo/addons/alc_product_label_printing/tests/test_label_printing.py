# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from unittest import mock

from odoo.fields import first
from odoo.tests.common import Form, TransactionCase


class TestLabelPrinting(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # create printer
        Printer = cls.env["printing.printer"].sudo()
        Printer.search([]).unlink()
        printer_server = (
            cls.env["printing.server"]
            .sudo()
            .create({"name": "Localhost", "address": "no_printing", "port": "1234"})
        )

        cls.toshiba_printer = Printer.create(
            {
                "name": "Toshiba printer",
                "system_name": "toshiba_printer",
                "code": "20",
                "type": "toshiba",
                "server_id": printer_server.id,
            }
        )

        cls.zebra_printer = Printer.create(
            {
                "name": "Zebra printer",
                "system_name": "zebra_printer",
                "code": "20",
                "type": "zebra",
                "server_id": printer_server.id,
            }
        )

        # Create Partner and customer
        cls.partner = cls.env["res.partner"].create({"name": "my b2c partner"})
        cls.customer = cls.partner.copy()

        # Create product
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product 1",
                "type": "product",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "uom_po_id": cls.env.ref("uom.product_uom_unit").id,
                "default_code": "TOR1",
                "tracking": "none",
            }
        )
        wh = cls.env["stock.warehouse"].search([])
        cls.location = wh[0].view_location_id
        cls.location.usage = "internal"
        cls.loc_customer = cls.env.ref("stock.stock_location_customers")

        cls.pick_type = cls.env.ref("stock.picking_type_out")
        cls.pick_type.code = "internal"

        # Create picking
        cls.picking = cls.env["stock.picking"].create(
            {
                "partner_id": cls.partner.id,
                "customer_id": cls.customer.id,
                "picking_type_id": cls.pick_type.id,
                "location_id": cls.location.id,
                "location_dest_id": cls.loc_customer.id,
            }
        )
        cls.move = cls.env["stock.move"].create(
            {
                "picking_id": cls.picking.id,
                "name": "Test move 1a",
                "product_id": cls.product.id,
                "product_uom": cls.product.uom_id.id,
                "product_uom_qty": 6,
                "location_id": cls.location.id,
                "location_dest_id": cls.loc_customer.id,
                "date": "2018-01-01 00:00:00",
            }
        )
        cls.move._action_confirm()
        cls.lot = cls.env["stock.lot"].create({"product_id": cls.product.id})

        # add some stock
        inventory_quant = cls.env["stock.quant"].create(
            {
                "location_id": cls.location.id,
                "product_id": cls.product.id,
                "inventory_quantity": 100,
                "lot_id": cls.lot.id,
            }
        )
        inventory_quant.action_apply_inventory()

        cls.picking.with_context(round_autoset=False).action_assign()
        for pack_op in cls.picking.move_line_ids:
            pack_op.qty_done = pack_op.reserved_uom_qty
        cls.picking.action_put_in_pack()

    def test_1(self):
        # Case 1 : partner wants the labels, customer is b2c : no labels should be printed
        self.picking.partner_id.no_labels_products = False
        self.picking.customer_id.is_b2c_customer = True
        with mock.patch.object(
            self.env["stock.move.line"].__class__, "print_product_label"
        ) as patched_print:
            self.picking.print_products_label()
            # expected result : no call to the print method
            self.assertEqual(patched_print.call_count, 0)

    def test_2(self):
        # Case 2 : partner wants the labels, customer is not b2c : labels should be printed
        self.picking.partner_id.no_labels_products = False
        self.picking.customer_id.is_b2c_customer = False
        # Check that the products labels are printed for b2c partners
        with mock.patch.object(
            self.env["stock.move.line"].__class__, "print_product_label"
        ) as patched_print:
            self.picking.print_products_label()
            # expected result : one call to the print method
            self.assertEqual(patched_print.call_count, 1)

    def test_3(self):
        # Case 3 : partner does not want the labels, customer is not b2c : labels should not be printed
        self.picking.partner_id.no_labels_products = True
        self.picking.customer_id.is_b2c_customer = False
        with mock.patch.object(
            self.env["stock.move.line"].__class__, "print_product_label"
        ) as patched_print:
            self.picking.print_products_label()
            # expected result : no call to the print method
            self.assertEqual(patched_print.call_count, 0)

    def test_4(self):
        # Case 4 : partner does want the labels, customer is b2c : labels should not be printed
        self.picking.partner_id.no_labels_products = True
        self.picking.customer_id.is_b2c_customer = True
        with mock.patch.object(
            self.env["stock.move.line"].__class__, "print_product_label"
        ) as patched_print:
            self.picking.print_products_label()
            # expected result : no call to the print method
            self.assertEqual(patched_print.call_count, 0)

    def test_5(self):
        # print for specific package...
        self.picking.partner_id.no_labels_products = False
        self.picking.customer_id.is_b2c_customer = False
        PrintingPrinter = self.env["printing.printer"].__class__
        package = first(self.picking.move_line_ids).result_package_id
        self.assertTrue(package)
        with mock.patch.object(
            PrintingPrinter, "print_document"
        ) as patched_print_document:
            self.picking.print_products_label(
                printer_id=self.toshiba_printer, packages=package
            )
            patched_print_document.assert_called_once()

        with mock.patch.object(
            PrintingPrinter, "print_document"
        ) as patched_print_document:
            self.picking.print_packages_label(
                printer_id=self.toshiba_printer, packages=package
            )
            patched_print_document.assert_called_once()

    def test_6_print_food_label(self):
        self.picking.customer_id.is_b2c_customer = True
        with mock.patch.object(
            self.env["stock.move.line"].__class__, "print_food_product_label"
        ) as patched_print:
            self.picking.print_food_products_label()
            self.assertEqual(patched_print.call_count, 1)

    def test_7_print_food_label_forced_from_picking(self):
        # We do not wants labels but we call it from a picking :
        # specific call ==> we force print
        self.picking.partner_id.no_labels_food_products = True
        with mock.patch.object(
            self.env["stock.move.line"].__class__, "print_food_product_label"
        ) as patched_print:
            self.picking.print_food_products_label()
            self.assertEqual(patched_print.call_count, 1)

    def test_wizard_print(self):
        # We do not wants labels but we call it from a picking :
        # specific call ==> we force print
        wizard = self.env["print.label"].create(
            {"label_type": "food_product", "printer_id": self.zebra_printer.id}
        )
        PrintingPrinter = self.env["printing.printer"].__class__
        # food product label
        with mock.patch.object(
            PrintingPrinter, "print_document"
        ) as patched_print_document:
            wizard.printer_id = self.zebra_printer
            wizard.move_line_ids = self.picking.move_line_ids
            wizard.label_type = "food_product"
            wizard.print_label()
            patched_print_document.assert_called_once()

        with mock.patch.object(
            PrintingPrinter, "print_document"
        ) as patched_print_document:
            wizard.printer_id = self.zebra_printer
            wizard.move_line_ids = False
            wizard.picking_ids = self.picking
            wizard.label_type = "food_product"
            wizard.print_label()
            patched_print_document.assert_called_once()
        # product label
        with mock.patch.object(
            PrintingPrinter, "print_document"
        ) as patched_print_document:
            wizard.printer_id = self.toshiba_printer
            wizard.move_line_ids = False
            wizard.picking_ids = self.picking
            wizard.label_type = "product"
            wizard.print_label()
            patched_print_document.assert_called_once()

        # lot label
        with mock.patch.object(
            PrintingPrinter, "print_document"
        ) as patched_print_document:
            wizard.printer_id = self.zebra_printer
            wizard.lot_ids = self.lot
            wizard.label_type = "lot"
            wizard.print_label()
            patched_print_document.assert_called_once()

    def test_print_wizard_lot(self):
        """Test wizard form default values for lot label."""
        PrintingPrinter = self.env["printing.printer"].__class__
        wizard_form = Form(
            self.env["print.label"].with_context(
                active_model=self.lot._name,
                active_ids=self.lot.ids,
                default_label_type="lot",
            )
        )
        wizard_form.printer_id = self.zebra_printer
        wizard = wizard_form.save()
        self.assertEqual(wizard.lot_ids, self.lot)
        self.assertEqual(wizard.label_type, "lot")
        with mock.patch.object(
            PrintingPrinter, "print_document"
        ) as patched_print_document:
            wizard.print_label()
            patched_print_document.assert_called_once()
