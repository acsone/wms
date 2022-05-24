# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase

from .common import AlcEshopNewsMixin


class TestAlcEshopNews(SavepointCase, AlcEshopNewsMixin):
    @classmethod
    def setUpClass(cls):
        super(TestAlcEshopNews, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        super(TestAlcEshopNews, cls)._init_news()

    def test_reset_image_reset_filename(self):
        self.news_all_langs.image = None
        self.assertFalse(self.news_all_langs.image_filename)

    def test_to_json(self):
        res = self.news_all_langs._to_json()
        self.assertListEqual(
            [self.news_all_langs_json_en, self.news_all_langs_json_fr], res,
        )

    def test_to_json_one_lang_on_record(self):
        self.news_all_langs.lang_ids = self.lang_fr
        res = self.news_all_langs._to_json()
        self.assertListEqual([self.news_all_langs_json_fr], res)

    def test_to_json_specific_lang(self):
        res = self.news_all_langs._to_json(self.lang_fr)
        self.assertListEqual([self.news_all_langs_json_fr], res)
