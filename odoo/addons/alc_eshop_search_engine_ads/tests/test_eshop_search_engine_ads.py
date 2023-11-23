import datetime

from odoo.addons.connector_search_engine.tests.test_all import TestBindingIndexBaseFake


class TestEshopSearchEngineAds(TestBindingIndexBaseFake):
    @classmethod
    def _prepare_index_values(cls, backend=None):
        backend = backend or cls.backend
        return {
            "name": "ads Index",
            "backend_id": backend.id,
            "model_id": cls.env.ref("alc_eshop_ads.model_alc_eshop_ads").id,
            "lang_id": cls.env.ref("base.lang_en").id,
            "serializer_type": "alc_eshop_ads",
        }

    @classmethod
    def setup_records(cls, backend=None):
        cls.EShopAds = cls.env["alc.eshop.ads"]
        backend = backend or cls.backend
        # ensure we only work with the index we'll create
        cls.se_index_model.search([]).unlink()
        # create an index for partner model
        cls.se_index = cls.se_index_model.create(cls._prepare_index_values(backend))
        date_start = cls._get_date()
        date_end = cls._get_date(day_offset=1)
        cls.adv_top_left = cls.EShopAds.create(
            {
                "name": "test",
                "date_start": date_start,
                "date_end": date_end,
                "display_slot": "top_left",
                "image": None,
            }
        )
        cls.adv_bottom_left = cls.EShopAds.create(
            {
                "name": "test",
                "date_start": date_start,
                "date_end": date_end,
                "display_slot": "bottom_left",
                "image": None,
            }
        )
        cls.all_ads = cls.EShopAds.search([])
        cls.all_ads.action_toggle_is_published()
        cls.all_ads._compute_binding_ids()

    @classmethod
    def _get_date(cls, day_offset=0):
        return datetime.date.today() + datetime.timedelta(days=day_offset)

    @classmethod
    def _expected_result(cls, ads):
        return {
            "id": ads.id,
            "allowed_roles": "is_alcyonnaire,is_alcyonnaire_under_contract,non_alcyonnaire",
            "name": ads.name,
            "date_start": ads.date_start.isoformat(),
            "date_end": ads.date_end.isoformat(),
            "site_url": ads.site_url or "",
            "display_time": ads.display_time,
            "display_slot": ads.display_slot,
            "file": None,
            "image": None,
        }

    def test_00(self):
        """Cron will export all new published ads."""
        self.backend.cron_synchronize_ads()
        self.assertEqual(self.adv_top_left.se_binding_ids.state, "to_export")
        with self.se_adapter.mocked_calls() as calls:
            self.se_index.generate_batch_sync_per_index()
            index_calls = list(filter(lambda c: c.get("method") == "index", calls))
            self.assertEqual(len(index_calls), 1)
            index_call = index_calls[0]
            self.assertEqual(len(index_call.get("args")), 2)
            msg1_args = list(
                filter(
                    lambda c: c.get("id") == self.adv_top_left.id,
                    index_call.get("args"),
                )
            )[0]
            self.assertDictEqual(msg1_args, self._expected_result(self.adv_top_left))
        self.assertEqual(self.adv_top_left.se_binding_ids.state, "done")

    def test_01(self):
        """Ads unchanged shouldn't be exported."""
        self.test_00()
        self.adv_top_left.action_synchronize_ads()
        self.assertEqual(self.adv_top_left.se_binding_ids.state, "done")

    def test_02(self):
        """Ads changed should be exported."""
        self.test_00()
        self.adv_top_left.name = "ads updated"
        self.adv_top_left.action_synchronize_ads()
        self.assertEqual(self.adv_top_left.se_binding_ids.state, "to_export")
        with self.se_adapter.mocked_calls() as calls:
            self.se_index.generate_batch_sync_per_index()
            index_calls = list(filter(lambda c: c.get("method") == "index", calls))
            self.assertEqual(len(index_calls), 1)
            index_call = index_calls[0]
            self.assertEqual(len(index_call.get("args")), 1)
            msg1_args = list(
                filter(
                    lambda c: c.get("id") == self.adv_top_left.id,
                    index_call.get("args"),
                )
            )[0]
            self.assertDictEqual(msg1_args, self._expected_result(self.adv_top_left))
        self.assertEqual(self.adv_top_left.se_binding_ids.state, "done")

    def test_03(self):
        """The cron should export only the changed ads."""
        self.test_00()
        self.adv_top_left.name = "ads updated"
        self.backend.cron_synchronize_ads()
        self.assertEqual(self.adv_top_left.se_binding_ids.state, "to_export")
        with self.se_adapter.mocked_calls() as calls:
            self.se_index.generate_batch_sync_per_index()
            index_calls = list(filter(lambda c: c.get("method") == "index", calls))
            self.assertEqual(len(index_calls), 1)
            index_call = index_calls[0]
            self.assertEqual(len(index_call.get("args")), 1)
            msg1_args = list(
                filter(
                    lambda c: c.get("id") == self.adv_top_left.id,
                    index_call.get("args"),
                )
            )[0]
            self.assertDictEqual(msg1_args, self._expected_result(self.adv_top_left))
        self.assertEqual(self.adv_top_left.se_binding_ids.state, "done")

    def test_04(self):
        """Unpublished ads should be deleted."""
        self.test_00()
        self.adv_top_left.action_toggle_is_published()
        self.assertFalse(self.adv_top_left.is_published)
        self.assertEqual(self.adv_top_left.se_binding_ids.state, "to_delete")

    def test_05(self):
        """Future ads should be deleted."""
        self.test_00()
        self.assertEqual(self.adv_top_left.se_binding_ids.state, "done")
        self.adv_top_left.write(
            {
                "date_start": self._get_date(day_offset=10),
                "date_end": self._get_date(day_offset=15),
            }
        )
        self.backend.cron_synchronize_ads()
        self.assertFalse(self.adv_top_left.is_published)
        self.assertEqual(self.adv_top_left.se_binding_ids.state, "to_delete")

    def test_06(self):
        """Past ads should be deleted."""
        self.test_00()
        self.assertEqual(self.adv_top_left.se_binding_ids.state, "done")
        self.adv_top_left.write(
            {
                "date_start": self._get_date(day_offset=-15),
                "date_end": self._get_date(day_offset=-10),
            }
        )
        self.backend.cron_synchronize_ads()
        self.assertFalse(self.adv_top_left.is_published)
        self.assertEqual(self.adv_top_left.se_binding_ids.state, "to_delete")

    def test_07(self):
        """Ads set to be recomputed after edit."""
        self.test_00()
        self.adv_top_left.name = "ads updated"
        self.assertEqual(self.adv_top_left.se_binding_ids.state, "to_recompute")
