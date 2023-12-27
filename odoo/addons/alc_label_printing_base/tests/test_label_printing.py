# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest import mock

from odoo.tests.common import TransactionCase


class TestLabelPrinting(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        Printer = cls.env["printing.printer"].sudo()
        Printer.search([]).unlink()
        printer_server = (
            cls.env["printing.server"]
            .sudo()
            .create({"name": "Localhost", "address": "no_printing", "port": "1234"})
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

        # Create Partner
        cls.partner = cls.env["res.partner"].create({"name": "test partner"})

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
        cls.package = cls.picking.action_put_in_pack()

    def test_print_pack_label(self):
        wizard = self.env["print.label"].create(
            {
                "printer_id": self.zebra_printer.id,
                "picking_ids": [(4, self.picking.id)],
                "label_type": "package",
            }
        )
        with mock.patch.object(
            self.zebra_printer.__class__, "print_document"
        ) as mock_print:
            wizard.print_label()
            mock_print.assert_called_once()
            content = mock_print.call_args[0][1]
            self.assertIn(self.package.name, content.decode())

    def test_partner_normalized_name(self):
        special_char_name = "àÀâÂäÄæÆçÇéÉèÈêÊëËîÎïÏôÔœŒùÙûÛüÜ«»€"
        normalized_name = "aAaAaAaeAEcCeEeEeEeEiIiIoOoeOEuUuUuU<<>>EUR"
        self.partner.name = special_char_name
        self.assertEqual(self.partner.name, special_char_name)
        self.assertEqual(self.partner.normalized_name, normalized_name)
        self.assertEqual(self.partner.normalized_display_name, normalized_name)
