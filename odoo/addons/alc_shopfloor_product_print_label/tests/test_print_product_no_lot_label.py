# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest import mock

from .common import TestPrintProductLotLabelCommon


class TestPrintProductNoLotLabel(TestPrintProductLotLabelCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.batch_not_lot = cls._create_picking_batch(
            [[cls.BatchProduct(product=cls.product_a, quantity=1)]]
        )
        cls._simulate_batch_selected(cls.batch_not_lot)

    def test_00_print_med_product_label(self):
        self.menu.sudo().med_label = True
        self.env.user.sudo().printing_product_label_printer_id = self.printer1
        move_line = self.batch_not_lot.move_line_ids[0]
        with mock.patch.object(
            self.env["product.product"].__class__, "print_product_label"
        ) as patched_print:
            self.service.dispatch(
                "print_label",
                params={
                    "picking_batch_id": self.batch_not_lot.id,
                    "move_line_id": move_line.id,
                },
            )
            # expected result : one call to the print method
            self.assertEqual(patched_print.call_count, 1)

    def test_01_print_food_product_label_no_lot(self):
        self.menu.sudo().food_label = True
        self.env.user.sudo().printing_product_label_printer_id = self.printer2
        move_line = self.batch_not_lot.move_line_ids[0]
        with mock.patch.object(
            self.env["stock.move.line"].__class__, "print_food_product_label"
        ) as patched_print:
            self.service.dispatch(
                "print_label",
                params={
                    "picking_batch_id": self.batch_not_lot.id,
                    "move_line_id": move_line.id,
                },
            )
            self.assertEqual(patched_print.call_count, 1)
