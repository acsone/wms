# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime

import mock

from odoo.addons.component.tests.common import SavepointComponentCase


class TestEShopAdsElasticsearch(SavepointComponentCase):
    @classmethod
    def setUpClass(cls):
        super(TestEShopAdsElasticsearch, cls).setUpClass()
        cls.backend_specific = cls.env.ref("connector_elasticsearch.backend_1")
        cls.eshop_ads_model = cls.env.ref("alc_eshop_ads.model_alc_eshop_ads")
        cls.eshop_ads_index_config = cls.env.ref(
            "alc_eshop_ads_elasticsearch.index_config_eshop_ads"
        )
        cls.SEIndex = cls.env["se.index"]
        cls.se_index_fr = cls.SEIndex.create(
            {
                "model_id": cls.eshop_ads_model.id,
                "lang_id": cls.env.ref("base.lang_fr_BE").id,
                "config_id": cls.eshop_ads_index_config.id,
                "backend_id": cls.backend_specific.id,
            }
        )
        cls.se_index_en = cls.SEIndex.create(
            {
                "model_id": cls.eshop_ads_model.id,
                "lang_id": cls.env.ref("base.lang_en").id,
                "config_id": cls.eshop_ads_index_config.id,
                "backend_id": cls.backend_specific.id,
            }
        )
        with cls.backend_specific.work_on("se.index", index=cls.se_index_fr) as work:
            cls.adapter = work.component(usage="se.backend.adapter")
        cls.EShopAds = cls.env["alc.eshop.ads"]

        date_start = date_end = cls._get_date()
        cls.adv_top_left = cls.EShopAds.create(
            dict(
                name="test",
                date_start=date_start,
                date_end=date_end,
                display_slot="top_left",
            )
        )
        cls.adv_bottom_left = cls.EShopAds.create(
            dict(
                name="test",
                date_start=date_start,
                date_end=date_end,
                display_slot="bottom_left",
            )
        )
        cls.adv_top_right_fr = cls.EShopAds.create(
            dict(
                name="test",
                date_start=date_start,
                date_end=date_end,
                display_slot="top_right",
                lang_id=cls.env.ref("base.lang_fr_BE").id,
            )
        )

        cls.adv_top_right_lang_en = cls.EShopAds.create(
            dict(
                name="test",
                date_start=date_start,
                date_end=date_end,
                display_slot="top_right",
                lang_id=cls.env.ref("base.lang_en_GB").id,
            )
        )
        cls.all_ads = cls.EShopAds.search([])

    @classmethod
    def _get_date(cls, day_offset=0):
        return datetime.date.today() + datetime.timedelta(days=day_offset)

    def test_export_only_lang(self):
        """Test that adds are exported according to the index lang"""
        with mock.patch.object(self.adapter.__class__, "index") as patched_index:
            self.adapter.put_ads(self.all_ads)
            patched_index.assert_called_once()
            json_docs = patched_index.call_args[0][0]
            self.assertEqual(len(json_docs), 3)
