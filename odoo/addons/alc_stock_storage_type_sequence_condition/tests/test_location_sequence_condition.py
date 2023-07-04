# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.fields import Command

from odoo.addons.stock_storage_type.tests.common import TestStorageTypeCommon


class TestAlcStorageTypeCondition(TestStorageTypeCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # As static library safe_eval.datetime is used, it is impossible
        # to mock that library - so, use some deltas from now
        cls.now = fields.Datetime.now()
        cls.sequence_cardboxes = cls.env.ref(
            "stock_storage_type.stock_package_storage_location_cardboxes"
        )
        cls.cond_stock = cls.env.ref(
            "alc_stock_storage_type_sequence_condition.condition_deja_stock"
        )
        cls.cond_lot = cls.env.ref(
            "alc_stock_storage_type_sequence_condition.condition_lot_en_stock"
        )
        cls.cond_reserve_lot = cls.env.ref(
            "alc_stock_storage_type_sequence_condition.condition_ancien_lot"
        )

        # configure a new sequence with none in the stock location (default destination)
        cls.cardboxes_package_storage_type.storage_location_sequence_ids.unlink()
        cls.warehouse.lot_stock_id.pack_putaway_strategy = "none"

        cls.alc_lot = cls.env["stock.lot"].create(
            {
                "name": "now + 2 months",
                "product_id": cls.product.id,
                "company_id": cls.env.company.id,
                "removal_date": cls.now + relativedelta(months=2),
            }
        )

        cls.alc_lot_old = cls.env["stock.lot"].create(
            {
                "name": "now + 1 month",
                "product_id": cls.product.id,
                "company_id": cls.env.company.id,
                "removal_date": cls.now + relativedelta(months=1),
            }
        )

        cls.alc_reserve_location = cls.env["stock.location"].create(
            {
                "name": "ALC Reserve",
                "location_id": cls.warehouse.view_location_id.id,
            }
        )

        cls.route = cls.env["stock.route"].create(
            {
                "name": "ALC Replenish",
                "rule_ids": [
                    Command.create(
                        {
                            "name": "ALC Reserve => Cardbox",
                            "location_src_id": cls.alc_reserve_location.id,
                            "location_dest_id": cls.cardboxes_location.id,
                            "picking_type_id": cls.env.ref(
                                "stock_location_orderpoint.stock_picking_type_replenish"
                            ).id,
                            "action": "pull",
                        }
                    )
                ],
            }
        )

        cls.env["stock.location.orderpoint"].create(
            {
                "location_id": cls.cardboxes_location.id,
                "route_id": cls.route.id,
            }
        )

    @classmethod
    def _create_same_stock_cond(cls):
        """Create Sequences for a same stock test."""
        cls.env["stock.storage.location.sequence"].create(
            {
                "package_type_id": cls.cardboxes_package_storage_type.id,
                "location_id": cls.cardboxes_bin_2_location.id,
                "sequence": 1,
                "location_sequence_cond_ids": [Command.set(cls.cond_stock.ids)],
            }
        )

        cls.env["stock.storage.location.sequence"].create(
            {
                "package_type_id": cls.cardboxes_package_storage_type.id,
                "location_id": cls.cardboxes_bin_4_location.id,
                "sequence": 2,
            }
        )

    @classmethod
    def _create_same_lot_cond(cls):
        """Create Sequences for a same stock test."""
        cls.env["stock.storage.location.sequence"].create(
            {
                "package_type_id": cls.cardboxes_package_storage_type.id,
                "location_id": cls.cardboxes_bin_1_location.id,
                "sequence": 1,
                "location_sequence_cond_ids": [Command.set(cls.cond_lot.ids)],
            }
        )

        cls.env["stock.storage.location.sequence"].create(
            {
                "package_type_id": cls.cardboxes_package_storage_type.id,
                "location_id": cls.cardboxes_bin_3_location.id,
                "sequence": 2,
            }
        )

    @classmethod
    def _create_reserve_lot_cond(cls):
        """Create Sequences for older lot in reserve."""
        cls.env["stock.storage.location.sequence"].create(
            {
                "package_type_id": cls.cardboxes_package_storage_type.id,
                "location_id": cls.cardboxes_bin_4_location.id,
                "sequence": 1,
                "location_sequence_cond_ids": [Command.set(cls.cond_reserve_lot.ids)],
            }
        )

        cls.env["stock.storage.location.sequence"].create(
            {
                "package_type_id": cls.cardboxes_package_storage_type.id,
                "location_id": cls.cardboxes_bin_1_location.id,
                "sequence": 2,
            }
        )

    def test_location_no_stock(self):
        """There is no stock in cardbox 2, so move will point out cardbox 4."""
        self._create_same_stock_cond()

        move = self._create_single_move(self.product)
        move._assign_picking()
        package = self.env["stock.quant.package"].create(
            {"product_packaging_id": self.product_lot_cardbox_product_packaging.id}
        )
        self._update_qty_in_location(
            move.location_id, move.product_id, move.product_qty, package=package
        )

        move._action_assign()
        move_line = move.move_line_ids
        package_level = move_line.package_level_id

        self.assertEqual(
            package_level.location_dest_id,
            self.cardboxes_bin_4_location,
            "the move line's destination must stay in Stock as we have"
            " a 'none' strategy on it and it is in the sequence",
        )

    def test_location_stock(self):
        """
        Create two location sequences for the cardbox package type.

            - The first one with a condition to have the same product
            - A second one without condition

        Update stock quantity in first location
        Move destination should be in that location
        """
        self._create_same_stock_cond()

        move = self._create_single_move(self.product)

        move._assign_picking()
        package = self.env["stock.quant.package"].create(
            {"product_packaging_id": self.product_lot_cardbox_product_packaging.id}
        )
        self._update_qty_in_location(
            move.location_id, move.product_id, move.product_qty, package=package
        )

        self.env["stock.quant"].with_context(inventory_mode=True).create(
            {
                "product_id": self.product.id,
                "inventory_quantity": 5.0,
                "location_id": self.cardboxes_bin_2_location.id,
            }
        )._apply_inventory()

        move._action_assign()
        move_line = move.move_line_ids
        package_level = move_line.package_level_id

        self.assertEqual(
            package_level.location_dest_id,
            self.cardboxes_bin_2_location,
            "the move line's destination must stay in Carboxes / Bin 2 as we have"
            " a 'none' strategy on Stock and a sequence with condition same product",
        )

    def test_location_no_lot(self):
        """
        Create two location sequences for the cardbox package type.

            - The first one with a condition to have the same product lot
            - A second one without condition

        Move destination should be in the second location
        """
        self._create_same_lot_cond()
        move = self._create_single_move(self.product)

        move._assign_picking()
        package = self.env["stock.quant.package"].create(
            {"product_packaging_id": self.product_lot_cardbox_product_packaging.id}
        )
        self._update_qty_in_location(
            move.location_id,
            move.product_id,
            move.product_qty,
            package=package,
            lot=self.alc_lot,
        )

        move._action_assign()
        move_line = move.move_line_ids
        package_level = move_line.package_level_id

        self.assertEqual(
            package_level.location_dest_id,
            self.cardboxes_bin_3_location,
            "the move line's destination must stay in Stock as we have"
            " a 'none' strategy on it and it is in the sequence",
        )

    def test_location_lot(self):
        """
        Create two location sequences for the cardbox package type.

            - The first one with a condition to have the same product lot
            - A second one without condition

        Update stock quantity in first location with the product and lot
        Move destination should be in the first location
        """
        self._create_same_lot_cond()
        move = self._create_single_move(self.product)

        move._assign_picking()
        package = self.env["stock.quant.package"].create(
            {"product_packaging_id": self.product_lot_cardbox_product_packaging.id}
        )
        self._update_qty_in_location(
            move.location_id,
            move.product_id,
            move.product_qty,
            package=package,
            lot=self.alc_lot,
        )

        self.env["stock.quant"].with_context(inventory_mode=True).create(
            {
                "product_id": self.product.id,
                "inventory_quantity": 5.0,
                "lot_id": self.alc_lot.id,
                "location_id": self.cardboxes_bin_1_location.id,
            }
        )._apply_inventory()

        move._action_assign()
        move_line = move.move_line_ids
        package_level = move_line.package_level_id

        self.assertEqual(
            package_level.location_dest_id,
            self.cardboxes_bin_1_location,
            "the move line's destination must stay in Stock as we have"
            " a 'none' strategy on it and it is in the sequence",
        )

    def test_location_younger_lot_in_reserve(self):
        """
        Create two location sequences for the cardbox package type.

            - The first one with a condition to don't have the older lot in reserve
            - A second one without condition

        Move destination should be in the second location
        """
        self._create_reserve_lot_cond()
        move = self._create_single_move(self.product)

        move._assign_picking()
        package = self.env["stock.quant.package"].create(
            {"product_packaging_id": self.product_lot_cardbox_product_packaging.id}
        )
        self._update_qty_in_location(
            move.location_id,
            move.product_id,
            move.product_qty,
            package=package,
            lot=self.alc_lot_old,
        )

        # Set product with lot in reserve with lot == '2023-05-01'
        self.env["stock.quant"].with_context(inventory_mode=True).create(
            {
                "product_id": self.product.id,
                "inventory_quantity": 5.0,
                "lot_id": self.alc_lot.id,
                "location_id": self.alc_reserve_location.id,
            }
        )._apply_inventory()

        move.lot_ids |= self.alc_lot_old
        move._action_assign()
        move_line = move.move_line_ids
        package_level = move_line.package_level_id

        self.assertEqual(
            package_level.location_dest_id,
            self.cardboxes_bin_4_location,
            "the move line's destination must stay in Stock as we have"
            " a 'none' strategy on it and it is in the sequence",
        )

    def test_location_older_lot_in_reserve(self):
        """
        Create two location sequences for the cardbox package type.

            - The first one with a condition to don't have the older lot in reserve
            - A second one without condition

        Move destination should be in the second location
        """
        self._create_reserve_lot_cond()
        move = self._create_single_move(self.product)

        move._assign_picking()
        package = self.env["stock.quant.package"].create(
            {"product_packaging_id": self.product_lot_cardbox_product_packaging.id}
        )
        self._update_qty_in_location(
            move.location_id,
            move.product_id,
            move.product_qty,
            package=package,
            lot=self.alc_lot,
        )

        # Set product with lot in reserve with lot == '2023-05-01'
        self.env["stock.quant"].with_context(inventory_mode=True).create(
            {
                "product_id": self.product.id,
                "inventory_quantity": 5.0,
                "lot_id": self.alc_lot_old.id,
                "location_id": self.alc_reserve_location.id,
            }
        )._apply_inventory()

        move.lot_ids |= self.alc_lot
        move._action_assign()
        move_line = move.move_line_ids
        package_level = move_line.package_level_id

        self.assertEqual(
            package_level.location_dest_id,
            self.cardboxes_bin_1_location,
            "the move line's destination must stay in Stock as we have"
            " a 'none' strategy on it and it is in the sequence",
        )
