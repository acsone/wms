# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.stock_storage_type.tests.common import TestStorageTypeCommon


class TestPutawayStorageTypeStrategy(TestStorageTypeCommon):
    @classmethod
    def setUpClass(cls):
        super(TestPutawayStorageTypeStrategy, cls).setUpClass()
        cls.areas.write({"pack_putaway_strategy": "ordered_locations"})

    def test_storage_strategy_none_in_sequence_to_fixes(self):
        """When a location has a strategy 'none' in sequence, stop

        We can use it to stop computing the put-away when the destination
        location match, In such a case, if the location match and a putaway
        rule is defined on the product for this destination location,
        the location destination will be the location from a call to the
        _get_product_putaway method on the location from the sequence

        This is very usefull to support fixed location putaway

        Ex:
        product putaway:
        * in: Cardboxes
        * out: cardboxes_bin_4_location

        sequence:
        1. Stock/Cardboxes: None

        If a move is created with destination "Stock", the put-away rule stops
        at sequence 1. Since a put away exists on the product for 'Cardboxes',
        the product putaway is applied and the final destination is
        'cardboxes_bin_4_location'

        """
        move = self._create_single_move(self.product)
        move.assign_picking()
        self.assertEqual(move.location_dest_id, self.stock_location)
        package = self.env["stock.quant.package"].create(
            {"product_packaging_id": self.product_lot_cardbox_product_packaging.id}
        )
        self._update_qty_in_location(
            move.location_id, move.product_id, move.product_qty, package=package
        )

        # configure a new sequence with none in the parent location
        self.cardboxes_package_storage_type.storage_location_sequence_ids.unlink()
        self.cardboxes_location.pack_putaway_strategy = "none"
        self.env["stock.storage.location.sequence"].create(
            {
                "package_storage_type_id": self.cardboxes_package_storage_type.id,
                "location_id": self.cardboxes_location.id,
                "sequence": 1,
            }
        )

        # create the putway from cardboxes to bin4
        self.env["product.stock.bin"].create(
            {
                "location_id": self.cardboxes_location.id,
                "bin_location_id": self.cardboxes_bin_4_location.id,
                "variant_id": self.product.id,
            }
        )

        move.action_assign()
        package_level = move.linked_move_operation_ids.operation_id

        self.assertEqual(
            package_level.location_dest_id, self.cardboxes_bin_4_location,
        )
