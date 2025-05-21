# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from unittest import mock

from odoo.addons.shopfloor.tests.test_cluster_picking_unload import (
    ClusterPickingUnloadingCommonCase,
)


# pylint: disable=missing-return
class ClusterPickingPutInPackPrintCase(ClusterPickingUnloadingCommonCase):
    @classmethod
    def setUpClassBaseData(cls, *args, **kwargs):
        super().setUpClassBaseData(*args, **kwargs)
        cls.bin1.write({"name": "bin1", "is_internal": True})
        cls.bin2.write({"name": "bin2", "is_internal": True})
        cls.menu.sudo().write({"pack_pickings": True, "print_on_pack_pickings": True})

        Printer = cls.env["printing.printer"].sudo()
        Printer.search([]).unlink()
        printer_server = (
            cls.env["printing.server"]
            .sudo()
            .create({"name": "Localhost", "address": "no_printing", "port": "1234"})
        )

        cls.product_label_printer = Printer.create(
            {
                "name": "Toshiba printer",
                "system_name": "toshiba_printer",
                "code": "20",
                "type": "toshiba",
                "server_id": printer_server.id,
            }
        )

        cls.package_label_printer = Printer.create(
            {
                "name": "Zebra printer",
                "system_name": "zebra_printer",
                "code": "20",
                "type": "zebra",
                "server_id": printer_server.id,
            }
        )

    def test_print_after_put_in_pack(self):
        move_lines = self.move_lines
        self._set_dest_package_and_done(move_lines[:1], self.bin2)
        self._set_dest_package_and_done(move_lines[1:], self.bin1)
        move_lines.write({"location_dest_id": self.packing_location.id})
        response = self.service.dispatch(
            "prepare_unload", params={"picking_batch_id": self.batch.id}
        )

        # The first bin to process is bin1 scan the pack and try to put in pack
        picking = move_lines[-1].picking_id
        data = self.data.pack_picking(picking)
        self.assert_response(
            response,
            next_state="pack_picking_scan_pack",
            data=data,
        )
        # we scan the pack
        response = self.service.dispatch(
            "scan_packing_to_pack",
            params={
                "picking_batch_id": self.batch.id,
                "picking_id": picking.id,
                "barcode": self.bin1.name,
            },
        )
        data = self.data.pack_picking(picking)
        self.assert_response(
            response,
            next_state="pack_picking_put_in_pack",
            data=data,
        )
        response = self.service.dispatch(
            "put_in_pack",
            params={
                "picking_batch_id": self.batch.id,
                "picking_id": picking.id,
                "selected_line_ids": move_lines.ids,
                "nbr_packages": 4,
            },
        )
        # No product printer defined...
        data = self.data.pack_picking(picking)
        self.assert_response(
            response,
            next_state="pack_picking_put_in_pack",
            data=data,
            message=self.service.msg_store.no_product_label_printer_found(),
        )
        self.env.user.sudo().printing_product_label_printer_id = (
            self.product_label_printer
        )
        response = self.service.dispatch(
            "put_in_pack",
            params={
                "picking_batch_id": self.batch.id,
                "picking_id": picking.id,
                "selected_line_ids": move_lines.ids,
                "nbr_packages": 4,
            },
        )
        # No package printer defined...
        data = self.data.pack_picking(picking)
        self.assert_response(
            response,
            next_state="pack_picking_put_in_pack",
            data=data,
            message=self.service.msg_store.no_package_label_printer_found(),
        )
        self.env.user.sudo().default_label_printer_id = self.package_label_printer

        # we process to the put in pack
        with (
            mock.patch.object(
                picking.__class__, "print_products_label"
            ) as mocked_print_product_label,
            mock.patch.object(
                picking.__class__, "print_packages_label"
            ) as mocked_print_package_label,
        ):
            self.service.dispatch(
                "put_in_pack",
                params={
                    "picking_batch_id": self.batch.id,
                    "selected_line_ids": move_lines.ids,
                    "picking_id": picking.id,
                    "nbr_packages": 4,
                },
            )
            mocked_print_product_label.assert_called_once()
            mocked_print_package_label.assert_called_once()

    def test_print_after_scan_destination_food(self):
        self.bin1.is_internal = True
        self.menu.sudo().write(
            {"pack_pickings": False, "print_on_pack_pickings": False}
        )
        move_line = self.batch.move_line_ids[0]
        qty_done = move_line.reserved_qty
        with mock.patch.object(
            move_line.__class__, "print_food_product_label"
        ) as mocked_print_food_product_label:
            self.service.dispatch(
                "scan_destination_pack",
                params={
                    "picking_batch_id": self.batch.id,
                    "move_line_id": move_line.id,
                    "barcode": self.bin1.name,
                    "quantity": qty_done,
                },
            )
            mocked_print_food_product_label.assert_called_once()

    def test_print_after_scan_destination_food_with_lot(self):
        self.product_a.tracking = "lot"
        initial_lot = self._create_lot(self.product_a)
        self.bin1.is_internal = True
        self.menu.sudo().write(
            {"pack_pickings": False, "print_on_pack_pickings": False}
        )
        move_line = self.batch.move_line_ids[0]
        # we need to put the lot on the move_line for this to work
        move_line.lot_id = initial_lot
        # self.env["stock.move.line"].create(vals)
        qty_done = move_line.reserved_qty
        with mock.patch.object(
            move_line.__class__, "print_food_product_label"
        ) as mocked_print_food_product_label:
            self.service.dispatch(
                "scan_destination_pack",
                params={
                    "picking_batch_id": self.batch.id,
                    "move_line_id": move_line.id,
                    "barcode": self.bin1.name,
                    "quantity": qty_done,
                    "lot_id": initial_lot.id,
                },
            )
            mocked_print_food_product_label.assert_called_once()

    def test_print_after_scan_destination_food_one_and_only_once(self):
        self.bin1.is_internal = True
        self.menu.sudo().write(
            {"pack_pickings": False, "print_on_pack_pickings": False}
        )
        pick1 = self.batch.picking_ids.filtered(lambda p: len(p.move_line_ids) == 2)
        move_lines1 = pick1.mapped("move_line_ids")
        self.assertEqual(len(move_lines1), 2)
        move_line = move_lines1[0]
        move_line.picking_id.partner_id.sudo().no_labels_food_products = True
        qty_done = move_line.reserved_qty
        self.assertFalse(move_line.picking_id.printed_once)
        with mock.patch.object(
            move_line.__class__, "print_food_product_label"
        ) as mocked_print_food_product_label:
            self.service.dispatch(
                "scan_destination_pack",
                params={
                    "picking_batch_id": self.batch.id,
                    "move_line_id": move_line.id,
                    "barcode": self.bin1.name,
                    "quantity": qty_done,
                },
            )
            mocked_print_food_product_label.assert_called_once()

        move_line2 = move_lines1[1]
        qty_done = move_line2.reserved_qty
        self.assertTrue(move_line2.picking_id.printed_once)
        with mock.patch.object(
            move_line2.__class__, "print_food_product_label"
        ) as mocked_print_food_product_label:
            self.service.dispatch(
                "scan_destination_pack",
                params={
                    "picking_batch_id": self.batch.id,
                    "move_line_id": move_line2.id,
                    "barcode": self.bin1.name,
                    "quantity": qty_done,
                },
            )
            mocked_print_food_product_label.assert_not_called()

        bin3 = self.env["stock.quant.package"].create(
            {"name": "bin3", "is_internal": True}
        )

        pick2 = self.batch.picking_ids.filtered(lambda p: len(p.move_line_ids) == 1)
        move_lines2 = pick2.mapped("move_line_ids")
        move_line3 = move_lines2[0]
        qty_done = move_line3.reserved_qty
        # Third op is on another picking : print again
        self.assertFalse(move_line3.picking_id.printed_once)
        with mock.patch.object(
            move_line3.__class__, "print_food_product_label"
        ) as mocked_print_food_product_label:
            self.service.dispatch(
                "scan_destination_pack",
                params={
                    "picking_batch_id": self.batch.id,
                    "move_line_id": move_line3.id,
                    "barcode": bin3.name,
                    "quantity": qty_done,
                },
            )
            mocked_print_food_product_label.assert_called_once()
        self.assertTrue(move_line3.picking_id.printed_once)

    def test_print_after_scan_destination_food_for_all_products(self):
        self.bin1.is_internal = True
        self.bin2.is_internal = True
        self.menu.sudo().write(
            {"pack_pickings": False, "print_on_pack_pickings": False}
        )
        move_line = self.batch.move_line_ids[0]
        qty_done = move_line.reserved_qty
        with mock.patch.object(
            move_line.__class__, "print_food_product_label"
        ) as mocked_print_food_product_label:
            self.service.dispatch(
                "scan_destination_pack",
                params={
                    "picking_batch_id": self.batch.id,
                    "move_line_id": move_line.id,
                    "barcode": self.bin1.name,
                    "quantity": qty_done,
                },
            )
            mocked_print_food_product_label.assert_called_once()

        move_line2 = self.batch.move_line_ids[1]
        qty_done = move_line2.reserved_qty
        with mock.patch.object(
            move_line2.__class__, "print_food_product_label"
        ) as mocked_print_food_product_label:
            self.service.dispatch(
                "scan_destination_pack",
                params={
                    "picking_batch_id": self.batch.id,
                    "move_line_id": move_line2.id,
                    "barcode": self.bin2.name,
                    "quantity": qty_done,
                },
            )
            mocked_print_food_product_label.assert_called_once()

    def test_errors_are_not_overwritten(self):
        """Here we give a package that is not on the move_line; this initial error should.

        bubble up, and not something else, like 'cannot print document'
        """
        self.product_a.tracking = "lot"
        self._create_lot(self.product_a)
        self.bin1.is_internal = True
        self.menu.sudo().write(
            {"pack_pickings": False, "print_on_pack_pickings": False}
        )
        move_line = self.batch.move_line_ids[0]
        qty_done = move_line.reserved_qty
        with mock.patch.object(
            move_line.__class__, "print_food_product_label"
        ) as mocked_print_food_product_label:
            result = self.service.dispatch(
                "scan_destination_pack",
                params={
                    "picking_batch_id": self.batch.id,
                    "move_line_id": move_line.id,
                    "barcode": self.bin1.name + "??",
                    "quantity": qty_done,
                },
            )
            message = result["message"]
            self.assertEqual(message["message_type"], "error")
            self.assertEqual("Bin bin1?? doesn't exist", message["body"])
            mocked_print_food_product_label.assert_not_called()
