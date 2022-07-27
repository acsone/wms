# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import mock

from odoo.addons.alc_shopfloor.tests.test_cluster_picking_base import (
    ClusterPickingCommonCase,
)


class TestPrintProductLotLabel(ClusterPickingCommonCase):
    @classmethod
    def setUpClass(cls):
        super(TestPrintProductLotLabel, cls).setUpClass()
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
                "type": "toshiba",
                "server_id": printer_server.id,
            }
        )

        cls.printer2 = Printer.create(
            {
                "name": "Test printer 2",
                "system_name": "test_printer_2",
                "type": "zebra",
                "server_id": printer_server.id,
            }
        )

        cls.profile_food = cls.env.ref("alc_shopfloor.shopfloor_profile_ali")
        cls.profile_medoc = cls.env.ref("alc_shopfloor.shopfloor_profile_medoc")

        cls.batch_not_lot = cls._create_picking_batch(
            [[cls.BatchProduct(product=cls.product_a, quantity=1)]]
        )
        cls._simulate_batch_selected(cls.batch_not_lot)

        cls.product_b.tracking = "lot"
        cls.product_lot = cls.env["stock.production.lot"].create(
            {"product_id": cls.product_b.id}
        )
        cls.batch_lot = cls._create_picking_batch(
            [[cls.BatchProduct(product=cls.product_b, quantity=1)]]
        )
        cls._simulate_batch_selected(cls.batch_lot)

    def test_00_print_med_product_label(self):
        self.menu.sudo().profile_id = self.profile_medoc.id
        self.shopfloor_user.sudo().printing_product_label_printer_id = self.printer1
        operation = self.batch_not_lot.pack_operation_ids[0]
        with mock.patch.object(
            self.env["product.product"].__class__, "print_product_label"
        ) as patched_print:
            self.service.dispatch(
                "print_label",
                params={
                    "picking_batch_id": self.batch_not_lot.id,
                    "operation_id": operation.id,
                },
            )
            # expected result : one call to the print method
            self.assertEqual(patched_print.call_count, 1)

    def test_01_print_med_lot_product_label(self):
        self.menu.sudo().profile_id = self.profile_medoc.id
        self.shopfloor_user.sudo().printing_product_label_printer_id = self.printer2
        operation = self.batch_lot.pack_operation_ids[0]
        with mock.patch.object(
            self.env["stock.production.lot"].__class__, "print_lot_label"
        ) as patched_print:
            self.service.dispatch(
                "print_label",
                params={
                    "picking_batch_id": self.batch_lot.id,
                    "operation_id": operation.id,
                    "lot_id": self.product_lot.id,
                },
            )
            self.assertEqual(patched_print.call_count, 1)

    def test_02_print_food_product_label_no_lot(self):
        self.menu.sudo().profile_id = self.profile_food.id
        self.shopfloor_user.sudo().printing_product_label_printer_id = self.printer2
        operation = self.batch_not_lot.pack_operation_ids[0]
        with mock.patch.object(
            self.env["stock.pack.operation"].__class__, "print_food_product_label"
        ) as patched_print:
            self.service.dispatch(
                "print_label",
                params={
                    "picking_batch_id": self.batch_not_lot.id,
                    "operation_id": operation.id,
                },
            )
            self.assertEqual(patched_print.call_count, 1)

    def test_03_print_food_product_label_lot(self):
        self.menu.sudo().profile_id = self.profile_food.id
        self.shopfloor_user.sudo().printing_product_label_printer_id = self.printer2
        operation = self.batch_lot.pack_operation_ids[0]
        with mock.patch.object(
            self.env["stock.pack.operation"].__class__, "print_food_product_label"
        ) as patched_print:
            self.service.dispatch(
                "print_label",
                params={
                    "picking_batch_id": self.batch_lot.id,
                    "operation_id": operation.id,
                    "lot_id": self.product_lot.id,
                },
            )
            self.assertEqual(patched_print.call_count, 1)
