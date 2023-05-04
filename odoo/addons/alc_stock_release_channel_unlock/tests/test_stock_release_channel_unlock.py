# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command

from odoo.addons.stock_release_channel.tests.common import ChannelReleaseCase


class TestStockReleaseChannelUnlock(ChannelReleaseCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tag_locked = cls.env.ref(
            "alc_stock_release_channel_tag.alc_stock_release_channel_tag_demo_1"
        )
        cls.tag_asleep = cls.env.ref(
            "alc_stock_release_channel_tag.alc_stock_release_channel_tag_demo_2"
        )
        cls.channel_open = cls.channel
        cls.channel_locked = cls.channel.copy({"state": "locked"})
        cls.channel_asleep = cls.channel.copy({"state": "asleep"})
        cls.channel_locked.stock_release_channel_tag_ids = cls.tag_locked
        cls.channel_asleep.stock_release_channel_tag_ids = cls.tag_asleep

    def _unlock_channel(self, tags):
        self.env["alc.stock.release.channel.unlock"].create(
            {"stock_release_channel_tag_ids": [Command.set(tags.ids)]}
        ).action_unlock()

    def test_00(self):
        """Test init context."""
        self.assertEqual(self.channel_open.state, "open")
        self.assertEqual(self.channel_locked.state, "locked")
        self.assertEqual(self.channel_asleep.state, "asleep")

    def test_01(self):
        self._unlock_channel(self.tag_locked)
        self.assertEqual(self.channel_open.state, "locked")
        self.assertEqual(self.channel_locked.state, "open")
        self.assertEqual(self.channel_asleep.state, "asleep")
        # nothing happens if we unlock the same tag
        self._unlock_channel(self.tag_locked)
        self.assertEqual(self.channel_open.state, "locked")
        self.assertEqual(self.channel_locked.state, "open")
        self.assertEqual(self.channel_asleep.state, "asleep")

    def test_02(self):
        self._unlock_channel(self.tag_asleep)
        self.assertEqual(self.channel_open.state, "locked")
        self.assertEqual(self.channel_locked.state, "locked")
        self.assertEqual(self.channel_asleep.state, "open")

    def test_03(self):
        self._unlock_channel(self.tag_locked | self.tag_asleep)
        self.assertEqual(self.channel_open.state, "locked")
        self.assertEqual(self.channel_locked.state, "open")
        self.assertEqual(self.channel_asleep.state, "open")
