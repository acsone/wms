# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.fields import Command
from odoo.tests.common import TransactionCase


class TestMissingInfoOnNewProduct(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.env = cls.env(
            context=dict(
                cls.env.context, tracking_disable=True, queue_job__no_delay=True
            )
        )
        cls.env["res.config.settings"].create(
            {"product_barcode_required": True}
        ).execute()
        storage_type_new = cls.env["stock.package.type"].create(
            {"name": "any name", "is_new": True}
        )
        cls.dummy_storage_type = cls.env["stock.package.type"].create({"name": "dummy"})
        cls.StockLocation = cls.env["stock.location"]
        cls.StockPicking = cls.env["stock.picking"]
        cls.ResPartner = cls.env["res.partner"]
        cls.pt1 = cls.env["product.template"].create(
            {
                "name": "Unittest missing dimensions and barcode",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "type": "product",
                "weight": 10.0,
                "package_type_id": storage_type_new.id,
            }
        )
        cls.p1 = cls.pt1.product_variant_ids[0]
        cls.pt2 = cls.env["product.template"].create(
            {
                "name": "Unittest missing dimensions and weight",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "type": "product",
                "barcode": "123456789",
                "package_type_id": storage_type_new.id,
            }
        )
        cls.p2 = cls.pt2.product_variant_ids[0]
        cls.pt3 = cls.env["product.template"].create(
            {
                "name": "Unittest missing barcode",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "type": "product",
                "weight": 10.0,
                "product_length": 2.0,
                "product_width": 4.0,
                "product_height": 6.0,
                "package_type_id": storage_type_new.id,
            }
        )
        cls.p3 = cls.pt3.product_variant_ids[0]
        cls.pt4 = cls.env["product.template"].create(
            {
                "name": "Unittest missing weight",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "type": "product",
                "product_length": 2.0,
                "product_width": 4.0,
                "product_height": 6.0,
                "barcode": "123456778",
                "package_type_id": storage_type_new.id,
            }
        )
        cls.p4 = cls.pt4.product_variant_ids[0]
        cls.pt5 = cls.env["product.template"].create(
            {
                "name": "Unittest missing dimensions",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "type": "product",
                "weight": 10.0,
                "barcode": "123456723",
                "package_type_id": storage_type_new.id,
            }
        )
        cls.p5 = cls.pt5.product_variant_ids[0]
        cls.pt6 = cls.env["product.template"].create(
            {
                "name": "Unittest weight and barcode",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "type": "product",
                "product_length": 2.0,
                "product_width": 4.0,
                "product_height": 6.0,
                "package_type_id": storage_type_new.id,
            }
        )
        cls.p6 = cls.pt6.product_variant_ids[0]
        cls.pt7 = cls.env["product.template"].create(
            {
                "name": "Unittest complete product",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "type": "product",
                "product_length": 2.0,
                "product_width": 4.0,
                "product_height": 6.0,
                "weight": 10.0,
                "barcode": "2345678910",
                "package_type_id": storage_type_new.id,
            }
        )
        cls.p7 = cls.pt7.product_variant_ids[0]
        cls.pt8 = cls.env["product.template"].create(
            {
                "name": "Unittest not new product",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "type": "product",
                "barcode": "23456998778910",
                "package_type_id": cls.dummy_storage_type.id,
            }
        )
        cls.p8 = cls.pt8.product_variant_ids[0]

        cls.pt9 = cls.env["product.template"].create(
            {
                "name": "Unittest is med product",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "type": "product",
                "weight": 10.0,
                "barcode": "234567998778910",
                "package_type_id": cls.dummy_storage_type.id,
            }
        )
        cls.p9 = cls.pt9.product_variant_ids[0]
        cls.p9.categ_id = cls.env.ref(
            "alc_product_category_data.product_categ_medoc"
        ).id

        cls.pt10 = cls.env["product.template"].create(
            {
                "name": "Unittest is food product",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "type": "product",
                "weight": 10.0,
                "barcode": "234569234578910",
                "package_type_id": cls.dummy_storage_type.id,
            }
        )
        cls.p10 = cls.pt10.product_variant_ids[0]
        cls.p10.categ_id = cls.env.ref("alc_product_food.product_categ_ali").id

        cls.pt11 = cls.env["product.template"].create(
            {
                "name": "Unittest is human product",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "type": "product",
                "weight": 10.0,
                "barcode": "2345696578778910",
                "is_human": True,
                "package_type_id": cls.dummy_storage_type.id,
            }
        )
        cls.p11 = cls.pt11.product_variant_ids[0]
        cls.p11.categ_id = cls.env.ref(
            "alc_product_category_data.product_categ_humain"
        ).id
        route_mto = cls.env.ref("stock.route_warehouse0_mto")
        route_mto.active = True
        route_mto.is_mto = True
        cls.pt13 = cls.env["product.template"].create(
            {
                "name": "Unittest is food mto product",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "type": "product",
                "weight": 10.0,
                "barcode": "23456920009578910",
                "package_type_id": cls.dummy_storage_type.id,
                "route_ids": [Command.set(route_mto.ids)],
            }
        )
        cls.p13 = cls.pt13.product_variant_ids[0]
        cls.p13.write(
            {
                "categ_id": cls.env.ref("alc_product_food.product_categ_ali").id,
            }
        )
        cls.product_box = cls.env["product.packaging"].create(
            {
                "name": "Box",
                "qty": 20,
                "product_id": cls.p11.id,
            }
        )

        cls.pt12 = cls.env["product.template"].create(
            {
                "name": "Unittest is mat product",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "type": "product",
                "weight": 10.0,
                "barcode": "2345696511178910",
                "is_equipment": True,
                "package_type_id": cls.dummy_storage_type.id,
            }
        )
        cls.p12 = cls.pt12.product_variant_ids[0]
        cls.p12.categ_id = cls.env.ref(
            "alc_product_category_data.product_categ_materiel"
        ).id

        cls.products = [
            cls.p1,
            cls.p2,
            cls.p3,
            cls.p4,
            cls.p5,
            cls.p6,
            cls.p7,
            cls.p8,
            cls.p9,
            cls.p10,
            cls.p11,
            cls.p12,
            cls.p13,
        ]
        cls.supplier = cls.ResPartner.create(
            {"name": "Unittest supplier", "ref": "839737475756467"}
        )

        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.reception_location = cls.StockLocation.create(
            {
                "name": "reception",
                "location_id": cls.stock_location.id,
                "usage": "view",
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
                "move_line_ids": [
                    Command.create(
                        {
                            "product_id": product.id,
                            "reserved_uom_qty": 5,
                            "product_uom_id": product.uom_id.id,
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
        cls.move_line_ids = cls.picking.move_line_ids
        cls.operation_missing_dimensions = cls.move_line_ids.search(
            [("product_id", "=", cls.p5.id)]
        )
        cls.operation_missing_barcode = cls.move_line_ids.search(
            [("product_id", "=", cls.p3.id)]
        )
        cls.operation_missing_weight = cls.move_line_ids.search(
            [("product_id", "=", cls.p4.id)]
        )
        cls.operation_missing_weight_dimensions = cls.move_line_ids.search(
            [("product_id", "=", cls.p2.id)]
        )
        cls.operation_not_new = cls.move_line_ids.search(
            [("product_id", "=", cls.p8.id)]
        )
        cls.operation_complete_product = cls.move_line_ids.search(
            [("product_id", "=", cls.p7.id)]
        )
        cls.operation_med_product = cls.move_line_ids.search(
            [("product_id", "=", cls.p9.id)]
        )
        cls.operation_food_product = cls.move_line_ids.search(
            [("product_id", "=", cls.p10.id)]
        )
        cls.operation_human_product = cls.move_line_ids.search(
            [("product_id", "=", cls.p11.id)]
        )
        cls.operation_mat_product = cls.move_line_ids.search(
            [("product_id", "=", cls.p12.id)]
        )
        cls.operation_food_mto_product = cls.move_line_ids.search(
            [("product_id", "=", cls.p13.id)]
        )
        cls.wiz = cls.receptionWizard.create(
            {
                "picking_id": cls.picking.id,
                "remaining_qty": 5,
                "qty": 1,
                "location_dest_id": cls.bin1.id,
            }
        )

        cls.env["res.config.settings"].create(
            {"reception_wizard_constraints": True}
        ).execute()

    def test_00_missing_dimensions(self):
        self.wiz.move_line_id = self.operation_missing_dimensions.id
        self.assertEqual(
            self.operation_missing_dimensions.product_id.name,
            "Unittest missing dimensions",
        )
        self.assertTrue(self.operation_missing_dimensions.product_id.is_new)
        self.assertTrue(self.operation_missing_dimensions.product_id.has_no_dimensions)
        error_msg = "You must enter dimensions for the product to receive"
        with self.assertRaises(ValidationError, msg=error_msg):
            self.wiz._check_dimensions_product()
        self.env["res.config.settings"].create(
            {"reception_wizard_constraints": False}
        ).execute()
        self.wiz._check_dimensions_product()

    def test_00_1_complete_dimensions(self):
        """
        Split the first test in 2 because the assertRaises does not completely roll back the transaction, leading to.

        object in some weird states and raising errors in gitlab
        """
        self.wiz.move_line_id = self.operation_missing_dimensions.id
        self.assertEqual(
            self.operation_missing_dimensions.product_id.name,
            "Unittest missing dimensions",
        )
        self.wiz.write({"product_length": 2, "product_width": 4, "product_height": 3})
        self.assertEqual(self.operation_missing_dimensions.product_id.product_length, 2)
        self.assertEqual(self.operation_missing_dimensions.product_id.product_width, 4)
        self.assertEqual(self.operation_missing_dimensions.product_id.product_height, 3)

    def test_01_missing_barcode(self):
        self.wiz.move_line_id = self.operation_missing_barcode.id
        self.assertEqual(
            self.operation_missing_barcode.product_id.name, "Unittest missing barcode"
        )
        error_msg = (
            "You must enter a barcode for the product to receive or allow "
            "the reception without barcode"
        )
        with self.assertRaises(ValidationError, msg=error_msg):
            self.wiz._check_barcode_new_product()

    def test_01_1_complete_barcode(self):
        """
        Split the first test in 2 because the assertRaises does not completely roll back the transaction, leading to.

        object in some weird states and raising errors in gitlab
        """
        self.wiz.move_line_id = self.operation_missing_barcode.id
        self.assertEqual(
            self.operation_missing_barcode.product_id.name, "Unittest missing barcode"
        )
        self.wiz.product_barcode = "986754321"
        self.assertEqual(self.operation_missing_barcode.product_id.barcode, "986754321")

    def test_02_missing_barcode_but_authorized(self):
        self.wiz.move_line_id = self.operation_missing_barcode.id
        self.assertEqual(
            self.operation_missing_barcode.product_id.name, "Unittest missing barcode"
        )
        error_msg = (
            "You must enter a barcode for the product to receive or allow "
            "the reception without barcode"
        )
        with self.assertRaises(ValidationError, msg=error_msg):
            self.wiz._check_barcode_new_product()

    def test_02_1_complete_barcode_but_authorized(self):
        """
        Split the first test in 2 because the assertRaises does not completely roll back the transaction, leading to.

        object in some weird states and raising errors in gitlab
        """
        self.wiz.move_line_id = self.operation_missing_barcode.id
        self.assertEqual(
            self.operation_missing_barcode.product_id.name, "Unittest missing barcode"
        )
        self.wiz.no_barcode_authorized = True
        self.assertFalse(self.operation_missing_barcode.product_id.barcode)
        self.assertTrue(self.operation_missing_barcode.product_id.no_barcode_authorized)

    def test_03_missing_weight(self):
        self.wiz.move_line_id = self.operation_missing_weight.id
        error_msg = "You must enter a weight for the product to receive"
        with self.assertRaises(ValidationError, msg=error_msg):
            self.wiz._check_weight_product()

    def test_03_1_complete_weight(self):
        """
        Split the first test in 2 because the assertRaises does not completely roll back the transaction, leading to.

        object in some weird states and raising errors in gitlab
        """
        self.wiz.move_line_id = self.operation_missing_weight.id
        self.assertEqual(
            self.operation_missing_weight.product_id.name, "Unittest missing weight"
        )
        self.wiz.product_weight = 10
        self.assertEqual(self.operation_missing_weight.product_id.weight, 10)

    def test_04_missing_weight_and_dimensions(self):
        self.wiz.move_line_id = self.operation_missing_weight_dimensions.id
        self.assertEqual(
            self.operation_missing_weight_dimensions.product_id.name,
            "Unittest missing dimensions and weight",
        )
        error_msg = "You must enter a weight for the product to receive"
        with self.assertRaises(ValidationError, msg=error_msg):
            self.wiz._check_weight_product()

    def test_04_1_missing_weight_and_dimensions(self):
        """
        Split the first test in 3 because the assertRaises does not completely roll back the transaction, leading to.

        object in some weird states and raising errors in gitlab
        """
        self.wiz.move_line_id = self.operation_missing_weight_dimensions.id
        self.assertEqual(
            self.operation_missing_weight_dimensions.product_id.name,
            "Unittest missing dimensions and weight",
        )
        error_msg = "You must enter dimensions for the product to receive"
        with self.assertRaises(ValidationError, msg=error_msg):
            self.wiz._check_dimensions_product()

    def test_04_2_complete_weight_and_dimensions(self):
        """
        Split the first test in 3 because the assertRaises does not completely roll back the transaction, leading to.

        object in some weird states and raising errors in gitlab
        """
        self.wiz.move_line_id = self.operation_missing_weight_dimensions.id
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
        self.assertEqual(
            self.operation_missing_weight_dimensions.product_id.product_length, 2
        )
        self.assertEqual(
            self.operation_missing_weight_dimensions.product_id.product_width, 4
        )

    def test_05_not_new_product(self):

        self.wiz.move_line_id = self.operation_not_new.id
        self.wiz.remaining_qty = 5
        self.wiz.qty = 1
        self.assertEqual(
            self.operation_not_new.product_id.name, "Unittest not new product"
        )
        self.wiz._add()
        self.assertEqual(self.operation_not_new.product_id.product_length, 0.0)
        self.assertEqual(self.operation_not_new.product_id.product_width, 0.0)
        self.assertEqual(self.operation_not_new.product_id.product_height, 0.0)
        self.assertTrue(self.operation_not_new.product_id.barcode)
        self.assertFalse(self.operation_not_new.product_id.no_barcode_authorized)
        self.assertEqual(self.operation_not_new.product_id.weight, 0.0)

    def test_06_no_info_missing(self):
        self.wiz.move_line_id = self.operation_complete_product.id
        self.wiz.remaining_qty = 5
        self.wiz.qty = 1
        self.assertEqual(
            self.operation_complete_product.product_id.name, "Unittest complete product"
        )
        self.wiz._add()

    def test_07_product_is_meds_missing_dimensions(self):
        self.wiz.move_line_id = self.operation_med_product.id
        self.assertEqual(
            self.operation_med_product.product_id.name,
            "Unittest is med product",
        )
        self.assertTrue(self.operation_med_product.product_id.is_meds)
        error_msg = "You must enter dimensions for the product to receive"
        with self.assertRaises(ValidationError, msg=error_msg):
            self.wiz._check_dimensions_product()

    def test_08_product_is_meds_complete_dimensions(self):
        self.wiz.move_line_id = self.operation_med_product.id
        self.assertEqual(
            self.operation_med_product.product_id.name,
            "Unittest is med product",
        )
        self.wiz.write({"product_length": 2, "product_width": 4, "product_height": 3})
        self.assertEqual(self.operation_med_product.product_id.product_length, 2)
        self.assertEqual(self.operation_med_product.product_id.product_width, 4)
        self.assertEqual(self.operation_med_product.product_id.product_height, 3)

    def test_09_product_is_food_missing_dimensions(self):
        self.wiz.move_line_id = self.operation_food_product.id
        self.assertEqual(
            self.operation_food_product.product_id.name,
            "Unittest is food product",
        )
        self.assertTrue(self.operation_food_product.product_id.is_food)
        error_msg = "You must enter dimensions for the product to receive"
        with self.assertRaises(ValidationError, msg=error_msg):
            self.wiz._check_dimensions_product()

    def test_10_product_is_food_complete_dimensions(self):
        self.wiz.move_line_id = self.operation_food_product.id
        self.assertEqual(
            self.operation_food_product.product_id.name,
            "Unittest is food product",
        )
        self.wiz.write({"product_length": 2, "product_width": 4, "product_height": 3})
        self.assertEqual(self.operation_food_product.product_id.product_length, 2)
        self.assertEqual(self.operation_food_product.product_id.product_width, 4)
        self.assertEqual(self.operation_food_product.product_id.product_height, 3)

    def test_11_product_is_human_missing_dimensions(self):
        self.wiz.move_line_id = self.operation_human_product.id
        self.assertEqual(
            self.operation_human_product.product_id.name,
            "Unittest is human product",
        )
        self.assertTrue(self.operation_human_product.product_id.is_human)
        error_msg = "You must enter dimensions for the product to receive"
        with self.assertRaises(ValidationError, msg=error_msg):
            self.wiz._check_dimensions_product()

    def test_12_product_is_human_complete_dimensions(self):
        self.wiz.move_line_id = self.operation_human_product.id
        self.assertEqual(
            self.operation_human_product.product_id.name,
            "Unittest is human product",
        )
        self.wiz.write({"product_length": 2, "product_width": 4, "product_height": 3})
        self.assertEqual(self.operation_human_product.product_id.product_length, 2)
        self.assertEqual(self.operation_human_product.product_id.product_width, 4)
        self.assertEqual(self.operation_human_product.product_id.product_height, 3)

    def test_13_product_is_human_update_packaging(self):
        self.wiz.move_line_id = self.operation_human_product.id
        self.assertEqual(
            self.operation_human_product.product_id.name,
            "Unittest is human product",
        )

        product_packaging = self.env["product.packaging"].create(
            {
                "name": "p11_packaging",
                "height": 10,
                "barcode": "11111112",
                "packaging_length": 10,
                "width": 10,
            }
        )
        self.p11.packaging_ids = [Command.set(product_packaging.ids)]
        self.wiz.write({"product_packaging_ids": [(6, 0, product_packaging.ids)]})

        self.assertEqual(
            self.operation_human_product.product_id.packaging_ids[0].packaging_length,
            10,
        )
        self.assertEqual(
            self.operation_human_product.product_id.packaging_ids[0].width, 10
        )
        self.assertEqual(
            self.operation_human_product.product_id.packaging_ids[0].height, 10
        )

    def test_14_product_is_med_create_packaging(self):
        self.wiz.move_line_id = self.operation_med_product.id

        product_box2 = self.env["product.packaging"].create(
            {
                "name": "Box test",
                "height": 10,
                "barcode": "1134553111112",
                "packaging_length": 10,
                "width": 10,
            }
        )
        self.wiz.write({"product_packaging_ids": [(6, 0, product_box2.ids)]})

        self.assertEqual(
            self.operation_med_product.product_id.packaging_ids[0].packaging_length, 10
        )
        self.assertEqual(
            self.operation_med_product.product_id.packaging_ids[0].width, 10
        )
        self.assertEqual(
            self.operation_med_product.product_id.packaging_ids[0].height, 10
        )
        self.assertEqual(
            self.operation_med_product.product_id.packaging_ids[0].barcode,
            "1134553111112",
        )

    def test_15_product_is_mat_missing_dimensions(self):
        self.wiz.move_line_id = self.operation_mat_product.id
        self.assertEqual(
            self.operation_mat_product.product_id.name,
            "Unittest is mat product",
        )
        self.assertTrue(self.operation_mat_product.product_id.is_equipment)
        error_msg = "You must enter dimensions for the product to receive"
        with self.assertRaises(ValidationError, msg=error_msg):
            self.wiz._check_dimensions_product()

    def test_16_product_is_mat_complete_dimensions(self):
        self.wiz.move_line_id = self.operation_mat_product.id
        self.assertEqual(
            self.operation_mat_product.product_id.name,
            "Unittest is mat product",
        )
        self.wiz.write({"product_length": 2, "product_width": 4, "product_height": 3})
        self.assertEqual(self.operation_mat_product.product_id.product_length, 2)
        self.assertEqual(self.operation_mat_product.product_id.product_width, 4)
        self.assertEqual(self.operation_mat_product.product_id.product_height, 3)

    def test_17_food_mto_product(self):
        self.wiz.move_line_id = self.operation_food_mto_product.id
        self.wiz.remaining_qty = 5
        self.wiz.qty = 1
        self.assertEqual(
            self.operation_food_mto_product.product_id.name,
            "Unittest is food mto product",
        )
        self.wiz._add()
