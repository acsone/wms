# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase

from ..schemas import Content
from .common import AlcEshopNewsMixin


class TestCmsContentLang(TransactionCase, AlcEshopNewsMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        super()._init_news()

    def test_iter_all_lang_on_record(self):
        records = list(self.news_all_langs._iter_by_lang())
        self.assertEqual(len(records), 2)
        self.assertEqual(len(records[0]), 1)
        expected_langs = {"en_US", "fr_FR"}
        received_langs = {records[0].env.lang}
        self.assertEqual(len(records[1]), 1)
        received_langs.add(records[1].env.lang)
        self.assertEqual(received_langs, expected_langs)

    def test_iter_one_lang_on_record(self):
        self.news_all_langs.lang_ids = self.lang_fr
        records = list(self.news_all_langs._iter_by_lang())
        self.assertEqual(len(records), 1)
        self.assertEqual(len(records[0]), 1)
        self.assertEqual(records[0].env.lang, "fr_FR")
        content = Content.from_odoo_record(records[0])
        self.assertListEqual(list(content.url_locales.keys()), ["fr"])

    def test_iter_specific_lang_on_record(self):
        records = list(self.news_all_langs._iter_by_lang(self.lang_fr))
        self.assertEqual(len(records), 1)
        self.assertEqual(len(records[0]), 1)
        self.assertEqual(records[0].env.lang, "fr_FR")
