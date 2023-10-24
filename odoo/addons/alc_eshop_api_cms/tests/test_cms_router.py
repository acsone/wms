# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.fastapi.tests.common import FastAPITransactionCase

from ..routers import cms_router
from ..schemas import Content
from .common import AlcEshopNewsMixin


class TestCmsRouter(FastAPITransactionCase, AlcEshopNewsMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        super()._init_news()
        cls.default_fastapi_router = cms_router
        cls.default_fastapi_authenticated_partner = None

    def test_all_contents(self):
        with self._create_test_client() as test_client:
            response = test_client.get("/cms/content")
        self.assertEqual(response.status_code, 200)
        res = response.json()
        self.assertTrue(res)
        self.assertIn(self.news_all_langs_json_fr, res["data"])
        self.assertIn(self.news_all_langs_json_en, res["data"])
        for record in self.eshop_snippet_product_on_order_cancel_intro._iter_by_lang():
            self.assertIn(Content.from_odoo_record(record).model_dump(), res["data"])
        for record in self.env.ref(
            "alc_eshop_cms.alc_eshop_cms_page_your-team-alcyon"
        )._iter_by_lang():
            self.assertIn(Content.from_odoo_record(record).model_dump(), res["data"])

    def test_all_contents_filter(self):
        with self._create_test_client() as test_client:
            response = test_client.get("/cms/content", params={"type": "snippet"})
        self.assertEqual(response.status_code, 200)
        res = response.json()
        self.assertTrue(res)
        self.assertEqual(res["size"], 3)
        with self._create_test_client() as test_client:
            response = test_client.get(
                "/cms/content", params={"type": "snippet", "lang": "fr"}
            )
        self.assertEqual(response.status_code, 200)
        res = response.json()
        self.assertEqual(res["size"], 1)
        expected = "Vous pouvez demander une modification des quantités"
        self.assertIn(expected, res["data"][0]["data"]["content"])

    def test_get_news_content(self):
        lang, content_type, url = self.news_all_langs_json_fr["url"].split("/")
        with self._create_test_client() as test_client:
            response = test_client.get(f"/cms/content/{lang}/{content_type}/{url}")
        self.assertEqual(response.status_code, 200)
        res = response.json()
        self.assertDictEqual(self.news_all_langs_json_fr, res)

    def test_get_snippet_content(self):
        snippet = self.eshop_snippet_product_on_order_cancel_intro.with_context(
            lang="fr_FR"
        )
        json_fr = Content.from_odoo_record(snippet).model_dump()
        lang, content_type, url = json_fr["url"].split("/")
        with self._create_test_client() as test_client:
            response = test_client.get(f"/cms/content/{lang}/{content_type}/{url}")
        self.assertEqual(response.status_code, 200)
        res = response.json()
        self.assertDictEqual(json_fr, res)

    def test_get_page_content(self):
        page = self.env.ref("alc_eshop_cms.alc_eshop_cms_page_about-us")
        page.lang_ids = self.lang_fr
        json_fr = Content.from_odoo_record(page.with_context(lang="fr_FR")).model_dump()
        lang, content_type, url = json_fr["url"].split("/")
        with self._create_test_client() as test_client:
            response = test_client.get(f"/cms/content/{lang}/{content_type}/{url}")
        self.assertEqual(response.status_code, 200)
        res = response.json()
        self.assertDictEqual(json_fr, res)
