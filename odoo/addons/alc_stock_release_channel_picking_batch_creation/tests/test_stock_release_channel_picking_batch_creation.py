# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.stock_picking_batch_creation.tests.common import (
    ClusterPickingCommonFeatures,
)


class TestStockReleaseChannelPickingBatchCreation(ClusterPickingCommonFeatures):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.p5 = cls._create_product("Unittest P5", 1, 4, 1, 1)
        cls.pickings = cls.pick1 | cls.pick2 | cls.pick3
        cls.channel = cls.env.ref("stock_release_channel.stock_release_channel_default")
        cls.make_picking_batch.release_channel_id = cls.channel
        cls.other_user = cls.env.ref("base.user_demo")
        cls.picking_type_1.release_channel_can_allow_pick = True
        cls.pickings.write({"release_channel_id": cls.channel.id})

    def test_00(self):
        """Test that if all condition satisfied the batch is created."""
        batch = self.make_picking_batch._create_batch()
        self.assertTrue(batch)
        self.assertEqual(self.pick3, batch.picking_ids)
        self.assertEqual(self.device3, batch.picking_device_id)

    def test_01(self):
        """Test that if picking is not assigned to a release channel will not be taken.

        in the batch
        """
        self.pickings.write({"release_channel_id": False})
        batch = self.make_picking_batch._create_batch()
        self.assertFalse(batch)

    def test_02(self):
        """Test that if release channel restrict usage for a user, pickings of other.

        users are not selected in the batch
        """
        self.channel.user_ids = self.other_user
        batch = self.make_picking_batch._create_batch()
        self.assertFalse(batch)

    def test_03(self):
        """Test that batch is not created if the release channel don't allow pick."""
        self.channel.pick_allowed = False
        batch = self.make_picking_batch._create_batch()
        self.assertFalse(batch)

    def test_04(self):
        """Test if picking type don't allow pick, its pickings are not taken in the.

        batch
        """
        self.channel._toggle_pick_allowed_for_picking_type_id(self.picking_type_1.id)
        batch = self.make_picking_batch._create_batch()
        self.assertFalse(batch)
        self.channel._toggle_pick_allowed_for_picking_type_id(self.picking_type_1.id)
        batch = self.make_picking_batch._create_batch()
        self.assertTrue(batch)

    def test_05(self):
        """Test that if picking type is not set to allow pick on release channel, its.

        pickings are not taken in the batch
        """
        self.picking_type_1.release_channel_can_allow_pick = False
        batch = self.make_picking_batch._create_batch()
        self.assertFalse(batch)

    def test_06(self):
        """Channel don't allow pick but on of picking types allow it."""
        self.channel._toggle_pick_allowed_channel()
        self.channel._toggle_pick_allowed_for_picking_type_id(self.picking_type_1.id)
        self.channel.pick_allowed = False
        self.assertFalse(self.channel.pick_allowed)
        self.assertTrue(
            self.channel._get_picking_type_pick_allowed(self.picking_type_1.id)
        )
        batch = self.make_picking_batch._create_batch()
        self.assertTrue(batch)

    def test_07(self):
        """Channel allow pick and no picking types allow it."""
        self.channel._toggle_pick_allowed_channel()
        self.channel.pick_allowed_by_picking_type = False
        picking_type_ids_pick_allowed = (
            self.channel._get_all_picking_type_ids_pick_allowed()
        )
        self.assertEqual(picking_type_ids_pick_allowed, [])
        self.assertFalse(self.channel.pick_allowed)
        self.assertFalse(
            self.channel._get_picking_type_pick_allowed(self.picking_type_1.id)
        )
        batch = self.make_picking_batch._create_batch()
        self.assertFalse(batch)
