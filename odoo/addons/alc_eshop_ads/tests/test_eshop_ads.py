# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError

from .common import TestEShopAdsCommon


class TestEShopAds(TestEShopAdsCommon):
    def test_create_simple(self):
        """Check simple creation."""
        date_start = date_end = self._get_date()
        adv_top_left = self.EShopAds.create(
            {
                "name": "test",
                "date_start": date_start,
                "date_end": date_end,
                "display_slot": "top_left",
                "image": self.image,
            }
        )
        self.assertTrue(adv_top_left)

    def test_create_dates(self):
        """Check date_end >= date_start."""
        date_start = self._get_date(+1)
        date_end = self._get_date(+4)
        with self.assertRaises(ValidationError):
            self.EShopAds.create(
                {
                    "name": "test",
                    "date_start": date_end,
                    "date_end": date_start,
                    "display_slot": "top_right",
                    "image": self.image,
                }
            )
