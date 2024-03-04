# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from freezegun import freeze_time

from odoo import Command, fields
from odoo.tests.common import TransactionCase


class TestStockReleaseChannelUnlock(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.channel = cls.env.ref("stock_release_channel.stock_release_channel_default")
        cls.tag_1 = cls.env.ref(
            "alc_stock_release_channel_tag.alc_stock_release_channel_tag_demo_1"
        )
        cls.tag_2 = cls.env.ref(
            "alc_stock_release_channel_tag.alc_stock_release_channel_tag_demo_2"
        )
        cls.preparation_plan_1 = cls.env.ref(
            "alc_stock_release_channel_preparation_plan."
            "alc_stock_release_channel_preparation_plan_demo_1"
        )
        cls.preparation_plan_2 = cls.env.ref(
            "alc_stock_release_channel_preparation_plan."
            "alc_stock_release_channel_preparation_plan_demo_2"
        )
        cls.channel_open_no_tag = cls.channel
        cls.channel_locked_tag_1 = cls.channel.copy()
        cls.channel_locked_tag_1.write(
            {
                "state": "locked",
                "stock_release_channel_tag_ids": [Command.set(cls.tag_1.ids)],
            }
        )
        cls.channel_asleep_tag_2 = cls.channel.copy()
        cls.channel_asleep_tag_2.write(
            {
                "state": "asleep",
                "stock_release_channel_tag_ids": [Command.set(cls.tag_2.ids)],
            }
        )
        cls.channel_asleep_plan_2_tag_2 = cls.channel.copy()
        cls.channel_asleep_plan_2_tag_2.write(
            {
                "state": "asleep",
                "stock_release_channel_tag_ids": [Command.set(cls.tag_2.ids)],
                "preparation_plan_ids": [Command.set(cls.preparation_plan_2.ids)],
            }
        )

    @freeze_time("2023-06-15 14:00:00")
    def _unlock_channel(self, tags, preparation_plan):
        self.env["alc.stock.release.channel.unlock"].create(
            {
                "preparation_plan_id": preparation_plan.id,
                "stock_release_channel_tag_ids": [Command.set(tags.ids)],
                "process_end_date": fields.Datetime.now(),
            }
        ).action_unlock()

    def test_00(self):
        """Test init context."""
        self.assertEqual(self.channel_open_no_tag.state, "open")
        self.assertEqual(self.channel_locked_tag_1.state, "locked")
        self.assertEqual(self.channel_asleep_tag_2.state, "asleep")

    def test_01(self):
        self._unlock_channel(self.tag_1, self.preparation_plan_1)
        self.assertEqual(self.channel_open_no_tag.state, "open")
        self.assertEqual(self.channel_locked_tag_1.state, "open")
        self.assertEqual(self.channel_asleep_tag_2.state, "asleep")
        # nothing happens if we unlock the same tag
        self._unlock_channel(self.tag_1, self.preparation_plan_1)
        self.assertEqual(self.channel_open_no_tag.state, "open")
        self.assertEqual(self.channel_locked_tag_1.state, "open")
        self.assertEqual(self.channel_asleep_tag_2.state, "asleep")

    def test_02(self):
        self.assertFalse(self.channel_asleep_tag_2.process_end_date)
        self._unlock_channel(self.tag_2, self.preparation_plan_1)
        self.assertEqual(self.channel_open_no_tag.state, "open")
        self.assertEqual(self.channel_locked_tag_1.state, "locked")
        self.assertEqual(self.channel_asleep_tag_2.state, "open")
        self.assertEqual(
            self.channel_asleep_tag_2.process_end_date,
            fields.Datetime.to_datetime("2023-06-15 00:00:00"),
        )

    def test_03(self):
        self._unlock_channel(self.tag_1 | self.tag_2, self.preparation_plan_1)
        self.assertEqual(self.channel_open_no_tag.state, "open")
        self.assertEqual(self.channel_locked_tag_1.state, "open")
        self.assertEqual(self.channel_asleep_tag_2.state, "open")

    def test_04(self):
        self._unlock_channel(self.tag_2, self.preparation_plan_2)
        self.assertEqual(self.channel_open_no_tag.state, "open")
        self.assertEqual(self.channel_locked_tag_1.state, "locked")
        self.assertEqual(self.channel_asleep_tag_2.state, "asleep")
        self.assertEqual(self.channel_asleep_plan_2_tag_2.state, "open")

    def test_process_end_date(self):
        self.channel_asleep_tag_2.process_end_time = 8.5
        self._unlock_channel(self.tag_2, self.preparation_plan_1)
        self.assertEqual(
            self.channel_asleep_tag_2.process_end_date,
            fields.Datetime.to_datetime("2023-06-15 08:30:00"),
        )
