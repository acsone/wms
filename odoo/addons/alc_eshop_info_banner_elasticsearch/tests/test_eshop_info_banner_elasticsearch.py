# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime

import mock

from odoo.addons.component.tests.common import SavepointComponentCase


class TestEShopInfoBannerElasticsearch(SavepointComponentCase):
    @classmethod
    def setUpClass(cls):
        super(TestEShopInfoBannerElasticsearch, cls).setUpClass()
        cls.backend_specific = cls.env.ref("connector_elasticsearch.backend_1")
        cls.eshop_info_banner_model = cls.env.ref(
            "alc_eshop_info_banner.model_alc_eshop_info_banner"
        )
        cls.eshop_info_banner_index_config = cls.env.ref(
            "alc_eshop_info_banner_elasticsearch.index_config_eshop_info_banner"
        )
        cls.SEIndex = cls.env["se.index"]
        cls.se_index_fr = cls.SEIndex.create(
            {
                "model_id": cls.eshop_info_banner_model.id,
                "lang_id": cls.env.ref("base.lang_fr_BE").id,
                "config_id": cls.eshop_info_banner_index_config.id,
                "backend_id": cls.backend_specific.id,
            }
        )
        cls.se_index_en = cls.SEIndex.create(
            {
                "model_id": cls.eshop_info_banner_model.id,
                "lang_id": cls.env.ref("base.lang_en").id,
                "config_id": cls.eshop_info_banner_index_config.id,
                "backend_id": cls.backend_specific.id,
            }
        )
        with cls.backend_specific.work_on("se.index", index=cls.se_index_fr) as work:
            cls.adapter = work.component(usage="se.backend.adapter")
        cls.EShopInfoBanner = cls.env["alc.eshop.info.banner"]

        date_start = cls._get_date()
        date_end = cls._get_date(day_offset=1)

        cls.msg_1 = cls.EShopInfoBanner.create(
            dict(
                html="<h1>Toto en</h1>",
                date_start=date_start,
                date_end=date_end,
                type="info",
            )
        )
        cls.msg_2 = cls.EShopInfoBanner.create(
            dict(
                html="<h1>Titi en</h1>",
                date_start=date_start,
                date_end=date_end,
                type="info",
            )
        )
        cls.all_info_banners = cls.EShopInfoBanner.search([])

    @classmethod
    def _get_date(cls, day_offset=0):
        return datetime.date.today() + datetime.timedelta(days=day_offset)

    def test_batch_export(self):
        indexes = self.se_index_en | self.se_index_en
        existing_jobs = self.env["queue.job"].search(
            [("method_name", "=", "export_info_banners")]
        )
        indexes.force_batch_export()
        new_jobs = (
            self.env["queue.job"].search([("method_name", "=", "export_info_banners")])
            - existing_jobs
        )
        self.assertEqual(1, len(new_jobs))

    def test_batch_export_backend(self):
        number_index = len(self.all_info_banners.mapped("se_index_ids"))
        with mock.patch.object(self.adapter.__class__, "index") as patched_index:
            self.backend_specific.cron_synchronize_info_banners()
            self.assertEqual(number_index, patched_index.call_count)

    def test_action_export(self):
        number_index = len(self.all_info_banners.mapped("se_index_ids"))
        with mock.patch.object(self.adapter.__class__, "index") as patched_index:
            self.all_info_banners.action_export_to_se()
            self.assertEqual(number_index, patched_index.call_count)
