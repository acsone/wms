# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime

from odoo.exceptions import ValidationError
from odoo.tests.common import SavepointCase


class TestEShopAds(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestEShopAds, cls).setUpClass()
        cls.EShopAds = cls.env["alc.eshop.ads"]

    @classmethod
    def _get_date(cls, day_offset=0):
        return datetime.date.today() + datetime.timedelta(days=day_offset)

    def test_create_no_overlaps(self):
        """Check that it's not possible to have 2 ads on the same
        period into the same slot."""
        date_start = date_end = self._get_date()
        adv_top_left = self.EShopAds.create(
            dict(
                name="test",
                date_start=date_start,
                date_end=date_end,
                display_slot="top_left",
            )
        )
        self.assertTrue(adv_top_left)
        # it's possible to create an ads for the same period in another slot
        adv_bottom_left = self.EShopAds.create(
            dict(
                name="test",
                date_start=date_start,
                date_end=date_end,
                display_slot="bottom_left",
            )
        )
        self.assertTrue(adv_bottom_left)
        # it's possible to create two ads for the same period and slot
        # but not the same lang
        adv_top_right_fr = self.EShopAds.create(
            dict(
                name="test",
                date_start=date_start,
                date_end=date_end,
                display_slot="top_right",
                lang_id=self.env.ref("base.lang_fr_BE").id,
            )
        )
        self.assertTrue(adv_top_right_fr)
        adv_top_right_lang_en = self.EShopAds.create(
            dict(
                name="test",
                date_start=date_start,
                date_end=date_end,
                display_slot="top_right",
                lang_id=self.env.ref("base.lang_en_GB").id,
            )
        )
        self.assertTrue(adv_top_right_lang_en)
        # it's not possible to create an ads that overlaps an other one
        # into the same slot
        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            date_start = self._get_date(-1)
            self.EShopAds.create(
                dict(
                    name="test",
                    date_start=date_start,
                    date_end=adv_top_left.date_end,
                    display_slot=adv_top_left.display_slot,
                )
            )
        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            date_end = self._get_date(+1)
            self.EShopAds.create(
                dict(
                    name="test",
                    date_start=adv_top_left.date_start,
                    date_end=date_end,
                    display_slot=adv_top_left.display_slot,
                )
            )
        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            # test case where existing has a not lang_id and created has a
            # lang_id
            date_end = self._get_date(+1)
            self.EShopAds.create(
                dict(
                    name="test",
                    date_start=adv_top_left.date_start,
                    date_end=date_end,
                    display_slot=adv_top_left.display_slot,
                    lang_id=self.env.ref("base.lang_en_GB").id,
                )
            )
        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            # test case where existing has a lang_id and created has not
            # lang_id
            date_end = self._get_date(+1)
            self.EShopAds.create(
                dict(
                    name="test",
                    date_start=adv_top_right_fr.date_start,
                    date_end=date_end,
                    display_slot=adv_top_right_fr.display_slot,
                )
            )
        # no onverlap another period is possible
        date_start = self._get_date(+1)
        date_end = self._get_date(+4)
        res = self.EShopAds.create(
            dict(
                name="test",
                date_start=date_start,
                date_end=date_end,
                display_slot="top_right",
            )
        )
        self.assertTrue(res)

    def test_create_dates(self):
        """Check date_end >= date_start"""
        date_start = self._get_date(+1)
        date_end = self._get_date(+4)
        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            self.EShopAds.create(
                dict(
                    name="test",
                    date_start=date_end,
                    date_end=date_start,
                    display_slot="top_right",
                )
            )
