# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.stock_storage_type.tests.common import TestStorageTypeCommon


class TestStorageTypePutawayStrategy(TestStorageTypeCommon):
    @classmethod
    def setUpClass(cls):
        super(TestStorageTypePutawayStrategy, cls).setUpClass()
        cls.areas.write({"pack_putaway_strategy": "ordered_locations"})

        cls.loc_bin = cls.env["stock.location"].create(
            {
                "name": "Bin",
                "location_id": cls.warehouse.lot_stock_id.id,
                "usage": "internal",
                "kind": "bin",
                "reserve_location_id": cls.cardboxes_location.id,
            }
        )
        # assign storage_type to product
        cls.product.product_package_storage_type_id = cls.cardboxes_package_storage_type
        # ensure tracking by lot
        cls.product.tracking = "lot"

        # declare a reserve location
        cls.cardboxes_bin_1_location.kind = "reserve"
        # put qties in reserve ...
        cls._update_qty_in_location(cls.cardboxes_bin_1_location, cls.product, 10)

    def test_01(self):
        """
        Data:
            a bin location with a reserve location from where
            a put_away strategy will take place and a child location declared
            as reserve with some product into
        Test Case:
            Create an internal picking with destination the bin location;
            confirm
        Expected result;
            The final location should not be a new the reserve location
            without product
        """
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.internal_picking_type.id,
                "location_id": self.suppliers_location.id,
                "location_dest_id": self.loc_bin.id,
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom_qty": 8.0,
                            "product_uom": self.product.uom_id.id,
                        },
                    )
                ],
            }
        )
        picking.action_confirm()
        self.assertEqual(
            picking.pack_operation_ids.mapped("location_dest_id"),
            self.cardboxes_bin_1_location,
        )
