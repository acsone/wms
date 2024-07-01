# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import datetime
import io

from PIL import Image

from odoo.addons.connector_search_engine.tests.test_all import TestBindingIndexBaseFake
from odoo.addons.fs_file.fields import FSFileValue
from odoo.addons.fs_image.fields import FSImageValue


class TestEshopSearchEngineAds(TestBindingIndexBaseFake):
    @classmethod
    def _create_image(cls, width, height, color="#4169E1", img_format="PNG"):
        f = io.BytesIO()
        Image.new("RGB", (width, height), color).save(f, img_format)
        f.seek(0)
        return f.read()

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
        # unlink existing storage
        cls.env["fs.storage"].search([]).unlink()
        # create our own storage
        cls.env["fs.storage"].create(
            {
                "name": "Temp FS Storage",
                "protocol": "memory",
                "code": "mem_dir",
                "directory_path": "/tmp/",
                "model_xmlids": "alc_eshop_ads.model_alc_eshop_ads",
                "base_url": "http://localhost:8069",
            }
        )
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
                "image": FSImageValue(name="test.png", value=cls._create_image(4, 2)),
                "file": FSFileValue(name="test.txt", value=b"test"),
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
        result = {
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
        if ads.file:
            result["file"] = {
                "url": ads.file.url,
                "name": ads.file.name,
                "mimetype": ads.file.mimetype,
            }
        if ads.image:
            result["image"] = {"name": ads.image.name, "url": ads.image.url}
        return result

    def test_00(self):
        """Cron will export all new published ads."""
        self.backend.button_synchronize_ads()
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
        self.backend.button_synchronize_ads()
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
        """Future ads should be kept."""
        self.test_00()
        self.assertEqual(self.adv_top_left.se_binding_ids.state, "done")
        self.adv_top_left.write(
            {
                "date_start": self._get_date(day_offset=10),
                "date_end": self._get_date(day_offset=15),
            }
        )
        self.backend.button_synchronize_ads()
        self.assertTrue(self.adv_top_left.is_published)
        self.assertEqual(self.adv_top_left.se_binding_ids.state, "to_recompute")

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
        self.backend.button_synchronize_ads()
        self.assertFalse(self.adv_top_left.is_published)
        self.assertEqual(self.adv_top_left.se_binding_ids.state, "to_delete")

    def test_07(self):
        """Ads set to be recomputed after edit."""
        self.test_00()
        self.adv_top_left.name = "ads updated"
        self.assertEqual(self.adv_top_left.se_binding_ids.state, "to_recompute")

    def test_lang_ads(self):
        # ads are exported into the right index according to their lang if
        # specified
        self.adv_top_left.lang_id = self.env.ref("base.lang_fr")
        self.adv_top_left.action_synchronize_ads()
        self.assertFalse(
            self.adv_top_left.se_binding_ids.filtered(lambda b: b.state != "to_delete")
        )
        index2_vals = self._prepare_index_values(self.backend)
        index2_vals.update(
            {"name": "Index 2", "lang_id": self.env.ref("base.lang_fr").id}
        )
        self.se_index_model.create(index2_vals)
        # we must recompute the se_index_ids field manually since we created
        # a new index
        self.adv_top_left._compute_se_index()
        self.adv_top_left.action_synchronize_ads()
        self.assertEqual(
            1,
            len(
                self.adv_top_left.se_binding_ids.filtered(
                    lambda b: b.state != "to_delete"
                )
            ),
        )
        self.adv_top_left.lang_id = None
        self.adv_top_left.action_synchronize_ads()
        self.assertEqual(
            2,
            len(
                self.adv_top_left.se_binding_ids.filtered(
                    lambda b: b.state != "to_delete"
                )
            ),
        )
        self.adv_top_left.lang_id = self.env.ref("base.lang_fr")
        self.adv_top_left.action_synchronize_ads()
        self.assertEqual(
            1,
            len(
                self.adv_top_left.se_binding_ids.filtered(
                    lambda b: b.state != "to_delete"
                    and b.index_id.lang_id == self.env.ref("base.lang_fr")
                )
            ),
        )
