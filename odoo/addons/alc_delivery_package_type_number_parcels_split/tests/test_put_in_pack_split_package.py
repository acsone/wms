# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError

from odoo.addons.stock.tests.test_packing import TestPackingCommon


class TestStockQuantPackageDelivery(TestPackingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.uom_kg = cls.env.ref("uom.product_uom_kgm")
        cls.product_test = cls.env["product.product"].create(
            {
                "name": "Product TEST",
                "type": "product",
                "weight": 0.1,
                "uom_id": cls.uom_kg.id,
                "uom_po_id": cls.uom_kg.id,
            }
        )
        test_carrier_product = cls.env["product.product"].create(
            {
                "name": "Test carrier product",
                "type": "service",
            }
        )
        cls.test_carrier = cls.env["delivery.carrier"].create(
            {
                "name": "Test carrier",
                "delivery_type": "fixed",
                "product_id": test_carrier_product.id,
            }
        )
        cls.package_type = cls.env["stock.package.type"].create(
            {
                "name": "package type",
                "number_of_parcels": 3,
                "auto_distribute_products_in_parcels": True,
            }
        )
        # put qty in stock
        cls.env["stock.quant"]._update_available_quantity(
            cls.product_test, cls.stock_location, 20.0
        )

        # create a shipping with 3 move lines of 2 products each
        cls.picking_ship = cls.env["stock.picking"].create(
            {
                "partner_id": cls.env["res.partner"].create({"name": "A partner"}).id,
                "picking_type_id": cls.warehouse.out_type_id.id,
                "location_id": cls.stock_location.id,
                "location_dest_id": cls.customer_location.id,
                "carrier_id": cls.test_carrier.id,
            }
        )
        cls.picking_ship.action_confirm()

        # create 3 move lines of 2 products each
        for _i in range(3):
            cls.env["stock.move.line"].create(
                {
                    "product_id": cls.product_test.id,
                    "product_uom_id": cls.product_test.uom_id.id,
                    "qty_done": 2.0,
                    "location_id": cls.stock_location.id,
                    "location_dest_id": cls.customer_location.id,
                    "picking_id": cls.picking_ship.id,
                }
            )

        pack_action = cls.picking_ship.action_put_in_pack()
        pack_action_ctx = pack_action["context"]
        pack_action_model = pack_action["res_model"]
        cls.pack_wizard = (
            cls.env[pack_action_model]
            .with_context(**pack_action_ctx)
            .create(
                {
                    "delivery_package_type_id": cls.package_type.id,
                }
            )
        )

    def test_with_more_move_lines_than_parcels(self):
        """Test the case where we have more move lines than parcels.

        We have:
          * 3 move lines
          * 2 parcels
        We should have:
            * 2 packages
            * 1 package with 2 move lines
            * 1 package with 1 move line
        """
        self.package_type.number_of_parcels = 2
        self.pack_wizard.action_put_in_pack()
        # check the number of packages created
        packages = self.picking_ship.package_ids
        self.assertEqual(len(packages), 2)
        # check that each move line is in a package
        result_package_ids = self.picking_ship.move_line_ids.result_package_id
        self.assertEqual(result_package_ids, packages)

    def test_with_more_parcels_than_move_lines_but_enough_qty(self):
        """Test the case where we have more parcels than move lines.

        but enough qty to fill the parcels.
        We have:
          * 3 move lines
          * 5 parcels
        We should have:
            * 5 packages
            * 5 move lines
        """
        qty_done = sum(self.picking_ship.move_line_ids.mapped("qty_done"))
        qty_reserved = sum(self.picking_ship.move_line_ids.mapped("reserved_uom_qty"))
        self.package_type.number_of_parcels = 5
        self.pack_wizard.action_put_in_pack()
        # check the number of packages created
        packages = self.picking_ship.package_ids
        self.assertEqual(len(packages), 5)
        # check that each move line is in a package
        result_package_ids = self.picking_ship.move_line_ids.result_package_id
        self.assertEqual(result_package_ids, packages)

        # check that at the end of the proces we have the same qty_done and reserved

        new_qty_done = sum(self.picking_ship.move_line_ids.mapped("qty_done"))
        new_qty_reserved = sum(
            self.picking_ship.move_line_ids.mapped("reserved_uom_qty")
        )
        self.assertEqual(qty_done, new_qty_done)
        self.assertEqual(qty_reserved, new_qty_reserved)

    def test_with_more_parcels_than_move_lines_but_same_as_qty(self):
        """Test the case where we have more parcels than move lines.

        same qty_done as the number of parcels.
        We have:
          * 3 move lines
          * 6 parcels
        We should have:
            * 6 packages
            * 6 move lines
        """
        qty_done = sum(self.picking_ship.move_line_ids.mapped("qty_done"))
        qty_reserved = sum(self.picking_ship.move_line_ids.mapped("reserved_uom_qty"))
        self.package_type.number_of_parcels = qty_done
        self.pack_wizard.action_put_in_pack()
        # check the number of packages created
        packages = self.picking_ship.package_ids
        self.assertEqual(len(packages), qty_done)
        # check that each move line is in a package
        result_package_ids = self.picking_ship.move_line_ids.result_package_id
        self.assertEqual(result_package_ids, packages)
        new_qty_done = sum(self.picking_ship.move_line_ids.mapped("qty_done"))
        new_qty_reserved = sum(
            self.picking_ship.move_line_ids.mapped("reserved_uom_qty")
        )
        self.assertEqual(qty_done, new_qty_done)
        self.assertEqual(qty_reserved, new_qty_reserved)

    def test_with_more_parcels_than_move_lines_but_not_enough_qty(self):
        """Test the case where we have more parcels than move lines.

        but not enough qty to fill the parcels.
        We have:
          * 3 move lines
          * 5 parcels
        We should have:
            * 5 packages
            * 5 move lines
        """
        qty_done = sum(self.picking_ship.move_line_ids.mapped("qty_done"))
        self.package_type.number_of_parcels = qty_done + 1
        with self.assertRaisesRegex(
            ValidationError,
            "The number of items to pack must be greater or equal to the number of parcels.",
        ):
            self.pack_wizard.action_put_in_pack()

    def test_with_no_parcels(self):
        """Test the case where we specify 0 parcels."""
        self.package_type.number_of_parcels = 0
        with self.assertRaisesRegex(
            ValidationError, "The number of parcels must be greater than 0."
        ):
            self.pack_wizard.action_put_in_pack()

        self.package_type.number_of_parcels = -1
        with self.assertRaisesRegex(
            ValidationError, "The number of parcels must be greater than 0."
        ):
            self.pack_wizard.action_put_in_pack()

        self.package_type.number_of_parcels = False
        with self.assertRaisesRegex(
            ValidationError, "The number of parcels must be greater than 0."
        ):
            self.pack_wizard.action_put_in_pack()

    def test_package_name(self):
        """When a put in pack creates multiple packages, all the packages.

        should have the same prefix and a different suffix.
        """
        self.package_type.number_of_parcels = 3
        self.pack_wizard.action_put_in_pack()
        # check the number of packages created
        packages = self.picking_ship.package_ids
        self.assertEqual(len(packages), 3)
        names = packages.mapped("name")

        prfxs = []
        sfxs = []
        for name in names:
            prfxs.append(name.split("_")[0])
            sfxs.append(name.split("_")[1])

        # all prefixes should be the same
        self.assertEqual(len(set(prfxs)), 1)
        # the suffixes should be a counter from 1 to 3
        self.assertEqual(len(set(sfxs)), 3)
        self.assertEqual(set(sfxs), {str(i) for i in range(1, 4)})
