# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime

from odoo.addons.connector_search_engine.tests.test_all import TestBindingIndexBaseFake


class TestEshopSearchEngineInfoBanner(TestBindingIndexBaseFake):
    @classmethod
    def _prepare_index_values(cls, backend=None):
        backend = backend or cls.backend
        return {
            "name": "Banner Index",
            "backend_id": backend.id,
            "model_id": cls.env.ref(
                "alc_eshop_info_banner.model_alc_eshop_info_banner"
            ).id,
            "lang_id": cls.env.ref("base.lang_en").id,
            "serializer_type": "alc_eshop_info_banner",
        }

    @classmethod
    def setup_records(cls, backend=None):
        cls.EShopInfoBanner = cls.env["alc.eshop.info.banner"]
        backend = backend or cls.backend
        # ensure we only work with the index we'll create
        cls.se_index_model.search([]).unlink()
        # create an index for partner model
        cls.se_index = cls.se_index_model.create(cls._prepare_index_values(backend))
        date_start = cls._get_date()
        date_end = cls._get_date(day_offset=1)
        cls.msg_1 = cls.EShopInfoBanner.create(
            {
                "html": "<h1>Toto en</h1>",
                "date_start": date_start,
                "date_end": date_end,
                "type": "info",
            }
        )
        cls.msg_2 = cls.EShopInfoBanner.create(
            {
                "html": "<h1>Titi en</h1>",
                "date_start": date_start,
                "date_end": date_end,
                "type": "info",
            }
        )
        cls.all_info_banners = cls.EShopInfoBanner.search([])
        cls.all_info_banners.action_toggle_is_published()
        cls.all_info_banners._compute_binding_ids()

    @classmethod
    def _get_date(cls, day_offset=0):
        return datetime.date.today() + datetime.timedelta(days=day_offset)

    @classmethod
    def _expected_result(cls, banner):
        return {
            "id": banner.id,
            "html": str(banner.html),
            "date_start": banner.date_start.isoformat(),
            "date_end": banner.date_end.isoformat(),
            "type": "info",
            "visibility": "auth_only",
        }

    def test_00(self):
        """Cron will export all new published banners."""
        self.backend.cron_synchronize_info_banners()
        self.assertEqual(self.msg_1.se_binding_ids.state, "to_export")
        with self.se_adapter.mocked_calls() as calls:
            self.se_index.generate_batch_sync_per_index()
            index_calls = list(filter(lambda c: c.get("method") == "index", calls))
            self.assertEqual(len(index_calls), 1)
            index_call = index_calls[0]
            self.assertEqual(len(index_call.get("args")), 2)
            msg1_args = next(
                iter(
                    filter(
                        lambda c: c.get("id") == self.msg_1.id, index_call.get("args")
                    )
                )
            )
            self.assertDictEqual(msg1_args, self._expected_result(self.msg_1))
        self.assertEqual(self.msg_1.se_binding_ids.state, "done")

    def test_01(self):
        """Banner unchanged shouldn't be exported."""
        self.test_00()
        self.msg_1.action_synchronize_records()
        self.assertEqual(self.msg_1.se_binding_ids.state, "done")

    def test_02(self):
        """Banner changed should be exported."""
        self.test_00()
        self.msg_1.html = "<h1>ok<h1/>"
        self.msg_1.action_synchronize_records()
        self.assertEqual(self.msg_1.se_binding_ids.state, "to_export")
        with self.se_adapter.mocked_calls() as calls:
            self.se_index.generate_batch_sync_per_index()
            index_calls = list(filter(lambda c: c.get("method") == "index", calls))
            self.assertEqual(len(index_calls), 1)
            index_call = index_calls[0]
            self.assertEqual(len(index_call.get("args")), 1)
            msg1_args = next(
                iter(
                    filter(
                        lambda c: c.get("id") == self.msg_1.id, index_call.get("args")
                    )
                )
            )
            self.assertDictEqual(msg1_args, self._expected_result(self.msg_1))
        self.assertEqual(self.msg_1.se_binding_ids.state, "done")

    def test_03(self):
        """The cron should export only the changed banner."""
        self.test_00()
        self.msg_1.html = "<h1>ok<h1/>"
        self.backend.cron_synchronize_info_banners()
        self.assertEqual(self.msg_1.se_binding_ids.state, "to_export")
        with self.se_adapter.mocked_calls() as calls:
            self.se_index.generate_batch_sync_per_index()
            index_calls = list(filter(lambda c: c.get("method") == "index", calls))
            self.assertEqual(len(index_calls), 1)
            index_call = index_calls[0]
            self.assertEqual(len(index_call.get("args")), 1)
            msg1_args = next(
                iter(
                    filter(
                        lambda c: c.get("id") == self.msg_1.id, index_call.get("args")
                    )
                )
            )
            self.assertDictEqual(msg1_args, self._expected_result(self.msg_1))
        self.assertEqual(self.msg_1.se_binding_ids.state, "done")

    def test_04(self):
        """Unpublished banner should be deleted."""
        self.test_00()
        self.msg_1.action_toggle_is_published()
        self.assertFalse(self.msg_1.is_published)
        self.assertEqual(self.msg_1.se_binding_ids.state, "to_delete")

    def test_05(self):
        """Future banner should be published."""
        self.test_00()
        self.assertEqual(self.msg_1.se_binding_ids.state, "done")
        self.msg_1.write(
            {
                "date_start": self._get_date(day_offset=10),
                "date_end": self._get_date(day_offset=15),
            }
        )
        self.backend.cron_synchronize_info_banners()
        self.assertTrue(self.msg_1.is_published)
        self.assertEqual(self.msg_1.se_binding_ids.state, "to_export")

    def test_06(self):
        """Past banner should be deleted."""
        self.test_00()
        self.assertEqual(self.msg_1.se_binding_ids.state, "done")
        self.msg_1.write(
            {
                "date_start": self._get_date(day_offset=-15),
                "date_end": self._get_date(day_offset=-10),
            }
        )
        self.backend.cron_synchronize_info_banners()
        self.assertFalse(self.msg_1.is_published)
        self.assertEqual(self.msg_1.se_binding_ids.state, "to_delete")

    def test_07(self):
        """Banner set to be recomputed after edit."""
        self.test_00()
        self.msg_1.html = "<h1>ok<h1/>"
        self.assertEqual(self.msg_1.se_binding_ids.state, "to_recompute")
