# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests.common import SavepointCase


class TestMissingInfoOnNewProduct(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestMissingInfoOnNewProduct, cls).setUpClass()

        cls.StockPicking = cls.env["stock.picking"]
        cls.receptionWizard = cls.env["stock.pack.operation.lot.add"]
        cls.StockLocation = cls.env["stock.location"]
        cls.ResPartner = cls.env["res.partner"]

        storage_type_new = cls.env.ref(
            "alc_stock_storage_type.package_st_M_M_Nouveaute", raise_if_not_found=False
        )

        cls.p1 = cls.env["product.product"].create(
            {
                "name": "Unittest missing dimensions and barcode",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
                "weight": 10.0,
            }
        )
        cls.p1.product_tmpl_id.product_package_storage_type_id = storage_type_new.id
        cls.p2 = cls.env["product.product"].create(
            {
                "name": "Unittest missing dimensions and weight",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
                "barcode": "123456789",
            }
        )
        cls.p2.product_tmpl_id.product_package_storage_type_id = storage_type_new.id
        cls.p3 = cls.env["product.product"].create(
            {
                "name": "Unittest missing barcode",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
                "weight": 10.0,
                "length": 2.0,
                "width": 4.0,
                "height": 6.0,
            }
        )
        cls.p3.product_tmpl_id.product_package_storage_type_id = storage_type_new.id
        cls.p4 = cls.env["product.product"].create(
            {
                "name": "Unittest missing weight",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
                "length": 2.0,
                "width": 4.0,
                "height": 6.0,
                "barcode": "123456778",
            }
        )
        cls.p4.product_tmpl_id.product_package_storage_type_id = storage_type_new.id
        cls.p5 = cls.env["product.product"].create(
            {
                "name": "Unittest missing dimensions",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
                "weight": 10.0,
                "barcode": "123456723",
            }
        )
        cls.p5.product_tmpl_id.product_package_storage_type_id = storage_type_new.id
        cls.p6 = cls.env["product.product"].create(
            {
                "name": "Unittest weight and barcode",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
                "length": 2.0,
                "width": 4.0,
                "height": 6.0,
            }
        )
        cls.p6.product_tmpl_id.product_package_storage_type_id = storage_type_new.id
        cls.p7 = cls.env["product.product"].create(
            {
                "name": "Unittest complete product",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
                "length": 2.0,
                "width": 4.0,
                "height": 6.0,
                "weight": 10.0,
                "barcode": "2345678910",
            }
        )
        cls.p7.product_tmpl_id.product_package_storage_type_id = storage_type_new.id
        cls.p8 = cls.env["product.product"].create(
            {
                "name": "Unittest not new product",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
                "weight": 10.0,
            }
        )
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

    def test_00_missing_dimensions(self):

        wiz = self.receptionWizard.create({"picking_id": self.picking.id})
        op = self.picking.pack_operation_product_ids[4]
        wiz.operation_id = op
        self.assertTrue(wiz.missing_product_dimensions)
        with self.assertRaises(UserError):
            wiz.button_nextop()
        wiz.write(
            {
                "product_length": 2,
                "product_width": 4,
                "product_height": 3,
                "qty": 1,
                "location_dest_id": self.bin1.id,
            }
        )

        wiz.button_nextop()

        product = op.product_id
        self.assertEqual(product.length, 2)
        self.assertEqual(product.width, 4)
        self.assertEqual(product.height, 3)

    def test_01_missing_barcode(self):

        wiz = self.receptionWizard.create({"picking_id": self.picking.id})
        op = self.picking.pack_operation_product_ids[2]
        wiz.operation_id = op
        self.assertTrue(wiz.missing_product_barcode)
        with self.assertRaises(UserError):
            wiz.button_nextop()
        wiz.write(
            {"product_barcode": "986754321", "qty": 1, "location_dest_id": self.bin1.id}
        )

        wiz.button_nextop()

        product = op.product_id
        self.assertEqual(product.barcode, "986754321")

    def test_02_missing_barcode_but_authorized(self):

        wiz = self.receptionWizard.create({"picking_id": self.picking.id})
        op = self.picking.pack_operation_product_ids[2]
        wiz.operation_id = op
        self.assertTrue(wiz.missing_product_barcode)
        with self.assertRaises(UserError):
            wiz.button_nextop()
        wiz.write(
            {"no_barcode_authorized": True, "qty": 1, "location_dest_id": self.bin1.id}
        )

        wiz.button_nextop()

        product = op.product_id
        self.assertFalse(product.barcode)
        self.assertTrue(product.no_barcode_authorized)

    def test_03_missing_weight(self):

        wiz = self.receptionWizard.create({"picking_id": self.picking.id})
        op = self.picking.pack_operation_product_ids[3]
        wiz.operation_id = op
        self.assertTrue(wiz.missing_product_weight)
        with self.assertRaises(UserError):
            wiz.button_nextop()
        wiz.write({"product_weight": 10, "qty": 1, "location_dest_id": self.bin1.id})

        wiz.button_nextop()

        product = op.product_id
        self.assertEqual(product.weight, 10)

    def test_04_missing_weight_and_dimensions(self):

        wiz = self.receptionWizard.create({"picking_id": self.picking.id})
        op = self.picking.pack_operation_product_ids[1]
        wiz.operation_id = op
        self.assertTrue(wiz.missing_product_weight)
        self.assertTrue(wiz.missing_product_dimensions)
        with self.assertRaises(UserError):
            wiz.button_nextop()

        wiz.write({"product_weight": 10, "qty": 1, "location_dest_id": self.bin1.id})

        with self.assertRaises(UserError):
            wiz.button_nextop()
        wiz.write(
            {
                "product_length": 2,
                "product_width": 4,
                "product_height": 3,
                "qty": 1,
                "location_dest_id": self.bin1.id,
            }
        )

        wiz.button_nextop()

        product = op.product_id
        self.assertEqual(product.length, 2)
        self.assertEqual(product.width, 4)
        self.assertEqual(product.height, 3)
        self.assertEqual(product.weight, 10)

    def test_05_missing_info_not_new_product(self):
        """
        Reception can be done if product is not new, even if info is missing
        """
        wiz = self.receptionWizard.create({"picking_id": self.picking.id})
        op = self.picking.pack_operation_product_ids[7]
        wiz.operation_id = op
        wiz.write({"qty": 1, "location_dest_id": self.bin1.id})
        wiz.button_nextop()

        product = op.product_id
        self.assertEqual(product.length, 0.0)
        self.assertEqual(product.width, 0.0)
        self.assertEqual(product.height, 0.0)
        self.assertFalse(product.barcode)
        self.assertEqual(product.weight, 10)

    def test_06_no_info_missing(self):
        wiz = self.receptionWizard.create({"picking_id": self.picking.id})
        op = self.picking.pack_operation_product_ids[6]
        wiz.operation_id = op
        self.assertFalse(wiz.missing_product_weight)
        self.assertFalse(wiz.missing_product_dimensions)
        self.assertFalse(wiz.missing_product_barcode)
        wiz.write({"qty": 1, "location_dest_id": self.bin1.id})
        wiz.button_nextop()
