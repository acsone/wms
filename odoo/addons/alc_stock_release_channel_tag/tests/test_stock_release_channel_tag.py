# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tools import mute_logger

from odoo.addons.stock_release_channel_geoengine.tests.common import (
    TestStockReleaseChannelGeoengineCommon,
)


class TestStockReleaseChannelTag(TestStockReleaseChannelGeoengineCommon):
    @classmethod
    @mute_logger("odoo.addons.stock_release_channel.models.stock_release_channel")
    def setUpClass(cls):
        super().setUpClass()
        cls.delivery_address_1.geo_point = cls.point1
        cls.delivery_address_2.geo_point = cls.point2
        cls.other_partner.geo_point = cls.point3
        cls.tag = cls.env.ref(
            "alc_stock_release_channel_tag.alc_stock_release_channel_tag_demo_1"
        )
        cls.channel.stock_release_channel_tag_ids = cls.tag
        cls.delivery_address_1.stock_release_channel_tag_ids = cls.tag

    @mute_logger("odoo.addons.stock_release_channel.models.stock_release_channel")
    def test_release_with_tag(self):
        self.pickings.assign_release_channel()
        self.assertEqual(self.picking.release_channel_id, self.channel)
        self.assertFalse(self.picking2.release_channel_id)
        self.assertFalse(self.picking3.release_channel_id)

    @mute_logger("odoo.addons.stock_release_channel.models.stock_release_channel")
    def test_release_without_tag(self):
        self.channel.stock_release_channel_tag_ids = False
        self.pickings.assign_release_channel()
        self.assertEqual(self.picking.release_channel_id, self.channel)
        self.assertEqual(self.picking2.release_channel_id, self.channel)
        self.assertEqual(self.picking3.release_channel_id, self.channel)
