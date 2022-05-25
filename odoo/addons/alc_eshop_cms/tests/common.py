# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
import datetime
import os


class CommonMixin(object):
    @classmethod
    def _init_langs(cls):
        if hasattr(cls, "all_langs"):
            return
        Langs = cls.env["res.lang"].with_context(active_test=False)
        cls.lang_fr = Langs.search([("code", "=", "fr_FR")])
        cls.lang_fr.active = True
        cls.env["ir.translation"].load_module_terms(["base"], [cls.lang_fr.code])
        cls.lang_en = cls.env["res.lang"]._lang_get("en_US")
        cls.all_langs = cls.lang_fr | cls.lang_en
        cls.eshop_snippet_product_on_order_cancel_intro = cls.env.ref(
            "alc_eshop_cms.alc_eshop_cms_snippet_product_on_order_cancel_intro"
        )
        cls.eshop_snippet_product_on_order_cancel_intro.write(
            {"lang_ids": [(6, 0, cls.all_langs.ids)]}
        )

    @classmethod
    def _get_date(cls, day_offset=0):
        return datetime.date.today() + datetime.timedelta(days=day_offset)

    @classmethod
    def _get_file(cls, name):
        path = os.path.dirname(os.path.abspath(__file__))
        f = open(os.path.join(path, "static", name))
        return base64.b64encode(f.read())


class AlcEshopNewsMixin(CommonMixin):
    @classmethod
    def _init_news(cls):
        res = super(AlcEshopNewsMixin, cls)._init_langs()
        cls.AlcEshopNews = cls.env["alc.eshop.cms.news"]
        cls.new_all_langs_vals = {
            "name": "name",
            "foreword": "<p>foreword</p>",
            "content": "<p>content</p>",
            "date_start": cls._get_date(),
            "date_end": cls._get_date(10),
            "thumbnail_image": cls._get_file("red.png"),
            "thumbnail_image_filename": "red.png",
            "image": cls._get_file("orange.png"),
            "image_filename": "orange.png",
            "file": cls._get_file("test.txt"),
            "filename": "test.txt",
            "lang_ids": [(6, 0, cls.all_langs.ids)],
        }
        cls.news_all_langs = cls.AlcEshopNews.create(cls.new_all_langs_vals)
        for lang in cls.all_langs:
            cls.news_all_langs.with_context(lang=lang.code).write(
                {
                    "name": cls.new_all_langs_vals["name"] + "-" + lang.code,
                    "foreword": "<p>foreword-%s</p>" % lang.code,
                    "content": "<p>content-%s</p>" % lang.code,
                }
            )

        cls.news_all_langs_json_en = {
            "url": u"en/news/name-en-us-%s" % cls.news_all_langs.id,
            "lang": u"en",
            "type": "news",
            "id": cls.news_all_langs.id,
            "data": {
                "foreword": "<p>foreword-en_US</p>",
                "title": u"name-en_US",
                "image": {
                    "url": cls.news_all_langs.image_id.url,
                    "name": u"orange.png",
                    "alt_name": None,
                },
                "content": "<p>content-en_US</p>",
                "file": {
                    "url": cls.news_all_langs.file_id.url,
                    "mimetype": u"text/plain",
                    "name": u"test.txt",
                },
                "thumbnail": {
                    "url": cls.news_all_langs.thumbnail_image_id.url,
                    "name": u"red.png",
                    "alt_name": None,
                },
            },
        }
        cls.news_all_langs_json_fr = {
            "url": u"fr/news/name-fr-fr-%s" % cls.news_all_langs.id,
            "lang": u"fr",
            "type": "news",
            "id": cls.news_all_langs.id,
            "data": {
                "foreword": "<p>foreword-fr_FR</p>",
                "title": u"name-fr_FR",
                "image": {
                    "url": cls.news_all_langs.image_id.url,
                    "name": u"orange.png",
                    "alt_name": None,
                },
                "content": "<p>content-fr_FR</p>",
                "file": {
                    "url": cls.news_all_langs.file_id.url,
                    "mimetype": u"text/plain",
                    "name": u"test.txt",
                },
                "thumbnail": {
                    "url": cls.news_all_langs.thumbnail_image_id.url,
                    "name": u"red.png",
                    "alt_name": None,
                },
            },
        }
        return res
