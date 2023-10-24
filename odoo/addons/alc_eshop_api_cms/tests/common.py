# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=missing-return

from odoo.addons.alc_eshop_cms.tests import common


class CommonMixin(common.CommonMixin):
    @classmethod
    def _init_fs_storage(cls):
        super()._init_fs_storage()
        cls.fs_storage.model_ids |= cls.env.ref("fs_image_thumbnail.model_fs_thumbnail")

    def setUp(self):
        super().setUp()
        self._init_fs_storage()


class AlcEshopNewsMixin(common.AlcEshopNewsMixin):
    def setUp(self):
        super().setUp()
        self._init_fs_storage()

    @classmethod
    def _init_fs_storage(cls):
        super()._init_fs_storage()
        cls.fs_storage.model_ids |= cls.env.ref("fs_image_thumbnail.model_fs_thumbnail")

    @classmethod
    def _init_news(cls):
        super()._init_news()
        cls.news_all_langs_json_en = {
            "url": f"en/news/name-en-us-{cls.news_all_langs.id}",
            "url_locales": {
                "fr": f"fr/news/name-fr-fr-{cls.news_all_langs.id}",
                "en": f"en/news/name-en-us-{cls.news_all_langs.id}",
            },
            "lang": "en",
            "type": "news",
            "id": cls.news_all_langs.id,
            "data": {
                "type": "news",
                "foreword": "<p>foreword-en_US</p>",
                "title": "name-en_US",
                "image": {
                    "url": cls.news_all_langs.image.url,
                    "name": "orange.png",
                    "alt_name": None,
                },
                "content": "<p>content-en_US</p>",
                "file": {
                    "url": cls.news_all_langs.file.url,
                    "mimetype": "text/plain",
                    "name": "test.txt",
                },
                "thumbnail": {
                    "url": cls.news_all_langs.thumbnail_image.url,
                    "name": "red.png",
                    "alt_name": None,
                },
            },
        }
        cls.news_all_langs_json_fr = {
            "url": f"fr/news/name-fr-fr-{cls.news_all_langs.id}",
            "url_locales": {
                "fr": f"fr/news/name-fr-fr-{cls.news_all_langs.id}",
                "en": f"en/news/name-en-us-{cls.news_all_langs.id}",
            },
            "lang": "fr",
            "type": "news",
            "id": cls.news_all_langs.id,
            "data": {
                "type": "news",
                "foreword": "<p>foreword-fr_FR</p>",
                "title": "name-fr_FR",
                "image": {
                    "url": cls.news_all_langs.image.url,
                    "name": "orange.png",
                    "alt_name": None,
                },
                "content": "<p>content-fr_FR</p>",
                "file": {
                    "url": cls.news_all_langs.file.url,
                    "mimetype": "text/plain",
                    "name": "test.txt",
                },
                "thumbnail": {
                    "url": cls.news_all_langs.thumbnail_image.url,
                    "name": "red.png",
                    "alt_name": None,
                },
            },
        }
