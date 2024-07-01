# Copyright 2020 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

# pylint: disable=missing-return

from odoo import Command

from odoo.addons.shopfloor.tests.common import CommonCase
from odoo.addons.stock.models.stock_move import PROCUREMENT_PRIORITIES

PRIORITY_NORMAL = PROCUREMENT_PRIORITIES[0][0]
PRIORITY_URGENT = PROCUREMENT_PRIORITIES[1][0]


class TestBatchCreate(CommonCase):
    @classmethod
    def setUpClassVars(cls, *args, **kwargs):
        super().setUpClassVars(*args, **kwargs)
        cls.menu = cls.env.ref("shopfloor.shopfloor_menu_demo_cluster_picking")
        cls.profile = cls.env.ref("shopfloor_base.profile_demo_1")
        cls.picking_type = cls.menu.picking_type_ids
        cls.wh = cls.picking_type.warehouse_id

    @classmethod
    def setUpClassBaseData(cls, *args, **kwargs):
        super().setUpClassBaseData()
        cls.picking1 = cls._create_picking(
            lines=[(cls.product_a, 10), (cls.product_b, 10)]
        )
        cls.picking2 = cls._create_picking(
            lines=[(cls.product_c, 10), (cls.product_d, 10)]
        )
        cls.picking3 = cls._create_picking(
            lines=[(cls.product_a, 10), (cls.product_b, 10)]
        )
        cls.picking4 = cls._create_picking(
            lines=[(cls.product_a, 10), (cls.product_b, 10)]
        )
        cls.pickings = cls.picking1 + cls.picking2 + cls.picking3 + cls.picking4
        cls._fill_stock_for_moves(cls.pickings.move_ids)
        cls.pickings.action_assign()
        cls.device = cls.env["stock.device.type"].create(
            {
                "name": "device",
                "min_volume": 0,
                "max_volume": 1000,
                "max_weight": 1000,
                "nbr_bins": 20,
                "sequence": 1,
            }
        )
        cls.menu.sudo().stock_device_type_ids = cls.device
        cls.channel = cls.env.ref("stock_release_channel.stock_release_channel_default")

    def setUp(self):
        super().setUp()
        self.service = self.get_service(
            "cluster_picking", profile=self.profile, menu=self.menu
        )
        with self.work_on_actions() as work:
            self.auto_batch = work.component(usage="picking.batch.auto.create")

    def test_00(self):
        """Normal case, no restriction."""
        self.shopfloor_user.only_one_release_channel_by_picking_batch = False
        batch = self.auto_batch.create_batch(
            self.picking_type,
            stock_device_types=self.device,
            maximum_number_of_preparation_lines=20,
            shopfloor_menu=self.menu,
        )
        self.assertEqual(batch.picking_ids, self.pickings)

    def test_00_bis(self):
        """Normal case, no restriction but requires a release channel set on the picking."""
        self.shopfloor_user.only_one_release_channel_by_picking_batch = False
        self.menu.sudo().release_channel_required = True
        batch = self.auto_batch.create_batch(
            self.picking_type,
            stock_device_types=self.device,
            maximum_number_of_preparation_lines=20,
            shopfloor_menu=self.menu,
        )
        self.assertFalse(batch.picking_ids)

    def test_01(self):
        """Restriction to same release channel but no picking released and not release channel required."""
        self.shopfloor_user.only_one_release_channel_by_picking_batch = True
        batch = self.auto_batch.create_batch(
            self.picking_type,
            stock_device_types=self.device,
            maximum_number_of_preparation_lines=20,
            shopfloor_menu=self.menu,
        )
        self.assertEqual(batch.picking_ids, self.pickings)

    def test_01_bis(self):
        """Restriction to same release channel but no picking released and release channel required."""
        self.shopfloor_user.only_one_release_channel_by_picking_batch = True
        self.menu.sudo().release_channel_required = True
        batch = self.auto_batch.create_batch(
            self.picking_type,
            stock_device_types=self.device,
            maximum_number_of_preparation_lines=20,
            shopfloor_menu=self.menu,
        )
        self.assertFalse(batch.picking_ids)

    def test_02(self):
        """Restriction to same release channel, all pickings are on the same channel."""
        self.shopfloor_user.only_one_release_channel_by_picking_batch = True
        self.pickings.write({"release_channel_id": self.channel.id})
        batch = self.auto_batch.create_batch(
            self.picking_type,
            stock_device_types=self.device,
            maximum_number_of_preparation_lines=20,
            shopfloor_menu=self.menu,
        )
        self.assertEqual(batch.picking_ids, self.pickings)

    def test_03(self):
        """Restriction to same release channel, some pickings are on the same channel."""
        self.shopfloor_user.only_one_release_channel_by_picking_batch = True
        released_pickings = self.picking1 | self.picking3
        released_pickings.write({"release_channel_id": self.channel.id})
        batch = self.auto_batch.create_batch(
            self.picking_type,
            stock_device_types=self.device,
            maximum_number_of_preparation_lines=20,
            shopfloor_menu=self.menu,
        )
        self.assertEqual(batch.picking_ids, released_pickings)

    def test_04(self):
        """Restriction to same release channel, some pickings are on different channels."""
        channel2 = self.channel.sudo().copy({"name": "channel 2"})
        self.shopfloor_user.only_one_release_channel_by_picking_batch = True
        released_pickings1 = self.picking1 | self.picking3
        released_pickings1.write({"release_channel_id": self.channel.id})
        released_pickings2 = self.picking2 | self.picking4
        released_pickings2.write({"release_channel_id": channel2.id})
        batch = self.auto_batch.create_batch(
            self.picking_type,
            stock_device_types=self.device,
            maximum_number_of_preparation_lines=20,
            shopfloor_menu=self.menu,
        )
        self.assertEqual(batch.picking_ids, released_pickings1)
        batch = self.auto_batch.create_batch(
            self.picking_type,
            stock_device_types=self.device,
            maximum_number_of_preparation_lines=20,
            shopfloor_menu=self.menu,
        )
        self.assertEqual(batch.picking_ids, released_pickings2)

    def test_05(self):
        """
        Restriction to same release channel and release channel required.

        the channel with user selected is picked first
        """
        user_channel = self.channel.sudo().copy(
            {
                "name": "channel 2",
                "user_ids": [Command.set(self.shopfloor_user.ids)],
                "state": "open",
            }
        )
        self.shopfloor_user.only_one_release_channel_by_picking_batch = True
        self.menu.sudo().release_channel_required = True
        released_pickings1 = self.picking1 | self.picking3
        released_pickings1.write({"release_channel_id": self.channel.id})
        released_pickings2 = self.picking2 | self.picking4
        released_pickings2.write({"release_channel_id": user_channel.id})
        batch = self.auto_batch.create_batch(
            self.picking_type,
            stock_device_types=self.device,
            maximum_number_of_preparation_lines=20,
            shopfloor_menu=self.menu,
        )
        self.assertEqual(batch.picking_ids.release_channel_id, user_channel)
        batch = self.auto_batch.create_batch(
            self.picking_type,
            stock_device_types=self.device,
            maximum_number_of_preparation_lines=20,
            shopfloor_menu=self.menu,
        )
        self.assertEqual(batch.picking_ids.release_channel_id, self.channel)
