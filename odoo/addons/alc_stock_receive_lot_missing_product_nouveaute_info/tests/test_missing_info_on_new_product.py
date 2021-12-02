# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.alc_product_is_new.tests.common import (
    ProductNewCharacteristicsCommonFeatures,
)

from ..exceptions import MissingBarcodeError, MissingDimensionsError, MissingWeightError


class TestMissingInfoOnNewProduct(ProductNewCharacteristicsCommonFeatures):
    @classmethod
    def setUpClass(cls):
        super(TestMissingInfoOnNewProduct, cls).setUpClass()

        cls.env = cls.env(
            context=dict(
                cls.env.context, tracking_disable=True, test_queue_job_no_delay=True
            )
        )
        cls.receptionWizard = cls.env["stock.pack.operation.lot.add"]
        cls.operation_ids = cls.picking.pack_operation_product_ids
        cls.operation_missing_dimensions = cls.operation_ids.search(
            [("product_id", "=", cls.p5.id)]
        )
        cls.operation_missing_barcode = cls.operation_ids.search(
            [("product_id", "=", cls.p3.id)]
        )
        cls.operation_missing_weight = cls.operation_ids.search(
            [("product_id", "=", cls.p4.id)]
        )
        cls.operation_missing_weight_dimensions = cls.operation_ids.search(
            [("product_id", "=", cls.p2.id)]
        )
        cls.operation_not_new = cls.operation_ids.search(
            [("product_id", "=", cls.p8.id)]
        )
        cls.operation_complete_product = cls.operation_ids.search(
            [("product_id", "=", cls.p7.id)]
        )

    def test_00_missing_dimensions(self):

        wiz = self.receptionWizard.create({"picking_id": self.picking.id})
        wiz.operation_id = self.operation_missing_dimensions.id
        self.assertEqual(
            self.operation_missing_dimensions.product_id.name,
            "Unittest missing dimensions",
        )
        self.assertTrue(self.operation_missing_dimensions.product_id.is_new)
        self.assertTrue(self.operation_missing_dimensions.product_id.has_no_dimensions)
        self.assertTrue(wiz.display_product_dimensions)
        wiz.write({"qty": 1, "location_dest_id": self.bin1.id})
        with self.assertRaises(MissingDimensionsError), self.env.cr.savepoint():
            wiz._add()

    def test_00_1_complete_dimensions(self):
        """
        Split the first test in 2 because the assertRaises does not completely roll back the transaction, leading to
        object in some weird states and raising errors in gitlab
        """
        wiz = self.receptionWizard.create({"picking_id": self.picking.id})
        wiz.operation_id = self.operation_missing_dimensions.id
        self.assertEqual(
            self.operation_missing_dimensions.product_id.name,
            "Unittest missing dimensions",
        )
        wiz.write(
            {
                "product_length": 2,
                "product_width": 4,
                "product_height": 3,
                "qty": 1,
                "location_dest_id": self.bin1.id,
            }
        )

        wiz._add()

        self.assertEqual(self.operation_missing_dimensions.product_id.length, 2)
        self.assertEqual(self.operation_missing_dimensions.product_id.width, 4)
        self.assertEqual(self.operation_missing_dimensions.product_id.height, 3)

    def test_01_missing_barcode(self):
        wiz = self.receptionWizard.create({"picking_id": self.picking.id})
        wiz.operation_id = self.operation_missing_barcode.id
        self.assertEqual(
            self.operation_missing_barcode.product_id.name, "Unittest missing barcode"
        )
        self.assertTrue(wiz.display_product_barcode)
        wiz.write({"qty": 1, "location_dest_id": self.bin1.id})
        with self.assertRaises(MissingBarcodeError), self.env.cr.savepoint():
            wiz._add()

    def test_01_1_complete_barcode(self):
        """
        Split the first test in 2 because the assertRaises does not completely roll back the transaction, leading to
        object in some weird states and raising errors in gitlab
        """
        wiz = self.receptionWizard.create({"picking_id": self.picking.id})
        wiz.operation_id = self.operation_missing_barcode.id
        self.assertEqual(
            self.operation_missing_barcode.product_id.name, "Unittest missing barcode"
        )
        wiz.write(
            {"product_barcode": "986754321", "qty": 1, "location_dest_id": self.bin1.id}
        )

        wiz._add()
        self.assertEqual(self.operation_missing_barcode.product_id.barcode, "986754321")

    def test_02_missing_barcode_but_authorized(self):
        wiz = self.receptionWizard.create({"picking_id": self.picking.id})
        wiz.operation_id = self.operation_missing_barcode.id
        self.assertEqual(
            self.operation_missing_barcode.product_id.name, "Unittest missing barcode"
        )
        self.assertTrue(wiz.display_product_barcode)
        wiz.write({"qty": 1, "location_dest_id": self.bin1.id})
        with self.assertRaises(MissingBarcodeError), self.env.cr.savepoint():
            wiz._add()

    def test_02_1_complete_barcode_but_authorized(self):
        """
        Split the first test in 2 because the assertRaises does not completely roll back the transaction, leading to
        object in some weird states and raising errors in gitlab
        """
        wiz = self.receptionWizard.create({"picking_id": self.picking.id})
        wiz.operation_id = self.operation_missing_barcode.id
        self.assertEqual(
            self.operation_missing_barcode.product_id.name, "Unittest missing barcode"
        )
        wiz.write(
            {"no_barcode_authorized": True, "qty": 1, "location_dest_id": self.bin1.id}
        )

        wiz._add()

        self.assertFalse(self.operation_missing_barcode.product_id.barcode)
        self.assertTrue(self.operation_missing_barcode.product_id.no_barcode_authorized)

    def test_03_missing_weight(self):
        wiz = self.receptionWizard.create({"picking_id": self.picking.id})
        wiz.operation_id = self.operation_missing_weight.id
        self.assertTrue(wiz.display_product_weight)
        wiz.write({"qty": 1, "location_dest_id": self.bin1.id})
        with self.assertRaises(MissingWeightError), self.env.cr.savepoint():
            wiz._add()

    def test_03_1_complete_weight(self):
        """
        Split the first test in 2 because the assertRaises does not completely roll back the transaction, leading to
        object in some weird states and raising errors in gitlab
        """
        wiz = self.receptionWizard.create({"picking_id": self.picking.id})
        wiz.operation_id = self.operation_missing_weight.id
        self.assertEqual(
            self.operation_missing_weight.product_id.name, "Unittest missing weight"
        )
        wiz.write({"product_weight": 10, "qty": 1, "location_dest_id": self.bin1.id})
        wiz._add()
        self.assertEqual(self.operation_missing_weight.product_id.weight, 10)

    def test_04_missing_weight_and_dimensions(self):
        wiz = self.receptionWizard.create({"picking_id": self.picking.id})
        wiz.operation_id = self.operation_missing_weight_dimensions.id
        self.assertEqual(
            self.operation_missing_weight_dimensions.product_id.name,
            "Unittest missing dimensions and weight",
        )
        self.assertTrue(wiz.display_product_weight)
        self.assertTrue(wiz.display_product_dimensions)
        wiz.write({"qty": 1, "location_dest_id": self.bin1.id})
        with self.assertRaises(MissingWeightError), self.env.cr.savepoint():
            wiz._add()

    def test_04_1_missing_weight_and_dimensions(self):
        """
        Split the first test in 3 because the assertRaises does not completely roll back the transaction, leading to
        object in some weird states and raising errors in gitlab
        """
        wiz = self.receptionWizard.create({"picking_id": self.picking.id})
        wiz.operation_id = self.operation_missing_weight_dimensions.id
        self.assertEqual(
            self.operation_missing_weight_dimensions.product_id.name,
            "Unittest missing dimensions and weight",
        )
        wiz.write({"product_weight": 10, "qty": 1, "location_dest_id": self.bin1.id})
        with self.assertRaises(MissingDimensionsError), self.env.cr.savepoint():
            wiz._add()

    def test_04_2_complete_weight_and_dimensions(self):
        """
        Split the first test in 3 because the assertRaises does not completely roll back the transaction, leading to
        object in some weird states and raising errors in gitlab
        """
        wiz = self.receptionWizard.create({"picking_id": self.picking.id})
        wiz.operation_id = self.operation_missing_weight_dimensions.id
        self.assertEqual(
            self.operation_missing_weight_dimensions.product_id.name,
            "Unittest missing dimensions and weight",
        )
        wiz.write(
            {
                "product_length": 2,
                "product_width": 4,
                "product_height": 3,
                "product_weight": 10,
                "qty": 1,
                "location_dest_id": self.bin1.id,
            }
        )
        wiz._add()
        self.assertEqual(self.operation_missing_weight_dimensions.product_id.length, 2)
        self.assertEqual(self.operation_missing_weight_dimensions.product_id.width, 4)
        self.assalc_stock_receive_lot_missing_product_nouveaute_infotion_id = (
            self.operation_not_new.id
        )
        self.assertEqual(
            self.operation_not_new.product_id.name, "Unittest not new product"
        )
        wiz.write({"qty": 1, "location_dest_id": self.bin1.id})
        wiz._add()

        self.assertEqual(self.operation_not_new.product_id.length, 0.0)
        self.assertEqual(self.operation_not_new.product_id.width, 0.0)
        self.assertEqual(self.operation_not_new.product_id.height, 0.0)
        self.assertFalse(self.operation_not_new.product_id.barcode)
        self.assertEqual(self.operation_not_new.product_id.weight, 10)

    def test_06_no_info_missing(self):
        wiz = self.receptionWizard.create({"picking_id": self.picking.id})
        wiz.operation_id = self.operation_complete_product.id
        self.assertEqual(
            self.operation_complete_product.product_id.name, "Unittest complete product"
        )
        self.assertFalse(wiz.display_product_weight)
        self.assertFalse(wiz.display_product_dimensions)
        self.assertFalse(wiz.display_product_barcode)
        wiz.write({"qty": 1, "location_dest_id": self.bin1.id})
        wiz._add()
