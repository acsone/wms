# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase

from ..exceptions import MissingBarcodeError, MissingDimensionsError, MissingWeightError


class TestMissingInfoOnNewProduct(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestMissingInfoOnNewProduct, cls).setUpClass()

        cls.env = cls.env(
            context=dict(
                cls.env.context, tracking_disable=True, test_queue_job_no_delay=True
            )
        )
        storage_type_new = cls.env.ref(
            "alc_stock_storage_type.package_st_M_M_Nouveaute"
        )
        cls.StockLocation = cls.env["stock.location"]
        cls.StockPicking = cls.env["stock.picking"]
        cls.ResPartner = cls.env["res.partner"]
        cls.pt1 = cls.env["product.template"].create(
            {
                "name": "Unittest missing dimensions and barcode",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
                "weight": 10.0,
                "product_package_storage_type_id": storage_type_new.id,
            }
        )
        cls.p1 = cls.pt1.product_variant_ids[0]
        cls.pt2 = cls.env["product.template"].create(
            {
                "name": "Unittest missing dimensions and weight",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
                "barcode": "123456789",
                "product_package_storage_type_id": storage_type_new.id,
            }
        )
        cls.p2 = cls.pt2.product_variant_ids[0]
        cls.pt3 = cls.env["product.template"].create(
            {
                "name": "Unittest missing barcode",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
                "weight": 10.0,
                "length": 2.0,
                "width": 4.0,
                "height": 6.0,
                "product_package_storage_type_id": storage_type_new.id,
            }
        )
        cls.p3 = cls.pt3.product_variant_ids[0]
        cls.pt4 = cls.env["product.template"].create(
            {
                "name": "Unittest missing weight",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
                "length": 2.0,
                "width": 4.0,
                "height": 6.0,
                "barcode": "123456778",
                "product_package_storage_type_id": storage_type_new.id,
            }
        )
        cls.p4 = cls.pt4.product_variant_ids[0]
        cls.pt5 = cls.env["product.template"].create(
            {
                "name": "Unittest missing dimensions",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
                "weight": 10.0,
                "barcode": "123456723",
                "product_package_storage_type_id": storage_type_new.id,
            }
        )
        cls.p5 = cls.pt5.product_variant_ids[0]
        cls.pt6 = cls.env["product.template"].create(
            {
                "name": "Unittest weight and barcode",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
                "length": 2.0,
                "width": 4.0,
                "height": 6.0,
                "product_package_storage_type_id": storage_type_new.id,
            }
        )
        cls.p6 = cls.pt6.product_variant_ids[0]
        cls.pt7 = cls.env["product.template"].create(
            {
                "name": "Unittest complete product",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
                "length": 2.0,
                "width": 4.0,
                "height": 6.0,
                "weight": 10.0,
                "barcode": "2345678910",
                "product_package_storage_type_id": storage_type_new.id,
            }
        )
        cls.p7 = cls.pt7.product_variant_ids[0]
        cls.pt8 = cls.env["product.template"].create(
            {
                "name": "Unittest not new product",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
                "barcode": "23456998778910",
            }
        )
        cls.p8 = cls.pt8.product_variant_ids[0]
        cls.products = [cls.p1, cls.p2, cls.p3, cls.p4, cls.p5, cls.p6, cls.p7, cls.p8]
        cls.supplier = cls.ResPartner.create(
            {"name": "Unittest supplier", "ref": "839737475756467"}
        )

        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.reception_location = cls.StockLocation.create(
            {
                "name": "reception",
                "location_id": cls.stock_location.id,
                "usage": "internal",
                "act_as_view": True,
            }
        )
        cls.bin1 = cls.StockLocation.create(
            {
                "name": "bin1",
                "location_id": cls.reception_location.id,
                "usage": "internal",
            }
        )
        cls.picking = cls.StockPicking.create(
            {
                "picking_type_id": cls.env.ref("stock.picking_type_in").id,
                "location_id": cls.supplier_location.id,
                "location_dest_id": cls.reception_location.id,
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": "move 1",
                            "product_id": product.id,
                            "product_uom_qty": 5,
                            "product_uom": product.uom_id.id,
                            "location_id": cls.supplier_location.id,
                            "location_dest_id": cls.reception_location.id,
                        },
                    )
                    for product in cls.products
                ],
            }
        )
        cls.picking.action_assign()

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

        cls.wiz = cls.receptionWizard.create(
            {"picking_id": cls.picking.id, "qty": 1, "location_dest_id": cls.bin1.id}
        )

    def test_00_missing_dimensions(self):
        self.wiz.operation_id = self.operation_missing_dimensions.id
        self.assertEqual(
            self.operation_missing_dimensions.product_id.name,
            "Unittest missing dimensions",
        )
        self.assertTrue(self.operation_missing_dimensions.product_id.is_new)
        self.assertTrue(self.operation_missing_dimensions.product_id.has_no_dimensions)
        with self.assertRaises(MissingDimensionsError), self.env.cr.savepoint():
            self.wiz._check_dimensions_new_product()

    def test_00_1_complete_dimensions(self):
        """
        Split the first test in 2 because the assertRaises does not completely roll back the transaction, leading to
        object in some weird states and raising errors in gitlab
        """
        self.wiz.operation_id = self.operation_missing_dimensions.id
        self.assertEqual(
            self.operation_missing_dimensions.product_id.name,
            "Unittest missing dimensions",
        )
        self.wiz.write({"product_length": 2, "product_width": 4, "product_height": 3})
        self.assertEqual(self.operation_missing_dimensions.product_id.length, 2)
        self.assertEqual(self.operation_missing_dimensions.product_id.width, 4)
        self.assertEqual(self.operation_missing_dimensions.product_id.height, 3)

    def test_01_missing_barcode(self):
        self.wiz.operation_id = self.operation_missing_barcode.id
        self.assertEqual(
            self.operation_missing_barcode.product_id.name, "Unittest missing barcode"
        )
        with self.assertRaises(MissingBarcodeError), self.env.cr.savepoint():
            self.wiz._check_barcode_new_product()

    def test_01_1_complete_barcode(self):
        """
        Split the first test in 2 because the assertRaises does not completely roll back the transaction, leading to
        object in some weird states and raising errors in gitlab
        """
        self.wiz.operation_id = self.operation_missing_barcode.id
        self.assertEqual(
            self.operation_missing_barcode.product_id.name, "Unittest missing barcode"
        )
        self.wiz.product_barcode = "986754321"
        self.assertEqual(self.operation_missing_barcode.product_id.barcode, "986754321")

    def test_02_missing_barcode_but_authorized(self):
        self.wiz.operation_id = self.operation_missing_barcode.id
        self.assertEqual(
            self.operation_missing_barcode.product_id.name, "Unittest missing barcode"
        )
        with self.assertRaises(MissingBarcodeError), self.env.cr.savepoint():
            self.wiz._check_barcode_new_product()

    def test_02_1_complete_barcode_but_authorized(self):
        """
        Split the first test in 2 because the assertRaises does not completely roll back the transaction, leading to
        object in some weird states and raising errors in gitlab
        """
        self.wiz.operation_id = self.operation_missing_barcode.id
        self.assertEqual(
            self.operation_missing_barcode.product_id.name, "Unittest missing barcode"
        )
        self.wiz.no_barcode_authorized = True
        self.assertFalse(self.operation_missing_barcode.product_id.barcode)
        self.assertTrue(self.operation_missing_barcode.product_id.no_barcode_authorized)

    def test_03_missing_weight(self):
        self.wiz.operation_id = self.operation_missing_weight.id
        with self.assertRaises(MissingWeightError), self.env.cr.savepoint():
            self.wiz._check_weight_new_product()

    def test_03_1_complete_weight(self):
        """
        Split the first test in 2 because the assertRaises does not completely roll back the transaction, leading to
        object in some weird states and raising errors in gitlab
        """
        self.wiz.operation_id = self.operation_missing_weight.id
        self.assertEqual(
            self.operation_missing_weight.product_id.name, "Unittest missing weight"
        )
        self.wiz.product_weight = 10
        self.assertEqual(self.operation_missing_weight.product_id.weight, 10)

    def test_04_missing_weight_and_dimensions(self):
        self.wiz.operation_id = self.operation_missing_weight_dimensions.id
        self.assertEqual(
            self.operation_missing_weight_dimensions.product_id.name,
            "Unittest missing dimensions and weight",
        )
        with self.assertRaises(MissingWeightError), self.env.cr.savepoint():
            self.wiz._check_weight_new_product()

    def test_04_1_missing_weight_and_dimensions(self):
        """
        Split the first test in 3 because the assertRaises does not completely roll back the transaction, leading to
        object in some weird states and raising errors in gitlab
        """
        self.wiz.operation_id = self.operation_missing_weight_dimensions.id
        self.assertEqual(
            self.operation_missing_weight_dimensions.product_id.name,
            "Unittest missing dimensions and weight",
        )
        with self.assertRaises(MissingDimensionsError), self.env.cr.savepoint():
            self.wiz._check_dimensions_new_product()

    def test_04_2_complete_weight_and_dimensions(self):
        """
        Split the first test in 3 because the assertRaises does not completely roll back the transaction, leading to
        object in some weird states and raising errors in gitlab
        """
        self.wiz.operation_id = self.operation_missing_weight_dimensions.id
        self.assertEqual(
            self.operation_missing_weight_dimensions.product_id.name,
            "Unittest missing dimensions and weight",
        )
        self.wiz.write(
            {
                "product_length": 2,
                "product_width": 4,
                "product_height": 3,
                "product_weight": 10,
            }
        )
        self.assertEqual(self.operation_missing_weight_dimensions.product_id.length, 2)
        self.assertEqual(self.operation_missing_weight_dimensions.product_id.width, 4)

    def test_05_not_new_product(self):

        self.wiz.operation_id = self.operation_not_new.id
        self.assertEqual(
            self.operation_not_new.product_id.name, "Unittest not new product"
        )
        self.wiz._add()
        self.assertEqual(self.operation_not_new.product_id.length, 0.0)
        self.assertEqual(self.operation_not_new.product_id.width, 0.0)
        self.assertEqual(self.operation_not_new.product_id.height, 0.0)
        self.assertTrue(self.operation_not_new.product_id.barcode)
        self.assertFalse(self.operation_not_new.product_id.no_barcode_authorized)
        self.assertEqual(self.operation_not_new.product_id.weight, 0.0)

    def test_06_no_info_missing(self):
        self.wiz.operation_id = self.operation_complete_product.id
        self.assertEqual(
            self.operation_complete_product.product_id.name, "Unittest complete product"
        )
        self.wiz._add()
