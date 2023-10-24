# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=missing-return

import base64
import datetime
import os


class CommonMixin:
    @classmethod
    def _init_langs(cls):
        if hasattr(cls, "all_langs"):
            return
        Langs = cls.env["res.lang"].with_context(active_test=False)
        cls.lang_fr = Langs.with_context(active_test=False).search(
            [("code", "=", "fr_FR")]
        )
        if not cls.lang_fr.active:
            cls.lang_fr.active = True
            # cls.lang_fr.toggle_active()
            # no toggle active to avoid to load all the translations
            # load translation only for the current module
            mod = cls.env["ir.module.module"].search(
                [("state", "=", "installed"), ("name", "=", "alc_eshop_cms")]
            )
            mod._update_translations("fr_FR")
        # disable others langs
        Langs.search([("code", "not in", ("en_US", "fr_FR"))]).active = False
        cls.lang_en = cls.env["res.lang"]._lang_get("en_US")
        cls.all_langs = cls.lang_fr | cls.lang_en
        cls.eshop_snippet_product_on_order_cancel_intro = cls.env.ref(
            "alc_eshop_cms.alc_eshop_cms_snippet_product_on_order_cancel_intro"
        )
        cls.eshop_snippet_product_on_order_cancel_intro.write(
            {"lang_ids": [(6, 0, cls.all_langs.ids)]}
        )
        cls.env["fs.storage"].search([]).unlink()
        cls.fs_storage = cls.env["fs.storage"].create(
            {
                "name": "Temp FS Storage",
                "protocol": "memory",
                "code": "mem_dir",
                "directory_path": "/tmp/",
            }
        )
        cls._init_fs_storage()

    @classmethod
    def _get_date(cls, day_offset=0):
        return datetime.date.today() + datetime.timedelta(days=day_offset)

    @classmethod
    def _get_file(cls, name):
        path = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(path, "static", name), "rb") as f:
            content = f.read()
        # return the content encoded in base64
        return base64.b64encode(content)

    @classmethod
    def _init_fs_storage(cls):
        cls.fs_storage.write(
            {
                "protocol": "memory",
                "directory_path": "/tmp/",
                "model_xmlids": "alc_eshop_cms.model_alc_eshop_cms_page,"
                "alc_eshop_cms.model_alc_eshop_cms_news,"
                "alc_eshop_cms.model_alc_eshop_cms_snippet",
                "base_url": "http://localhost:8069",
            }
        )


class AlcEshopNewsMixin(CommonMixin):
    @classmethod
    def _init_news(cls):
        super()._init_langs()
        cls.AlcEshopNews = cls.env["alc.eshop.cms.news"]
        cls.new_all_langs_vals = {
            "name": "name",
            "foreword": "<p>foreword</p>",
            "content": "<p>content</p>",
            "date_start": cls._get_date(),
            "date_end": cls._get_date(10),
            "thumbnail_image": {
                "filename": "red.png",
                "content": cls._get_file("red.png"),
            },
            "image": {
                "filename": "orange.png",
                "content": cls._get_file("orange.png"),
            },
            "file": {"filename": "test.txt", "content": cls._get_file("test.txt")},
            "lang_ids": [(6, 0, cls.all_langs.ids)],
        }
        cls.news_all_langs = cls.AlcEshopNews.create(cls.new_all_langs_vals)
        for lang in cls.all_langs:
            cls.news_all_langs.with_context(lang=lang.code).write(
                {
                    "name": cls.new_all_langs_vals["name"] + "-" + lang.code,
                    "foreword": f"<p>foreword-{lang.code}</p>",
                    "content": f"<p>content-{lang.code}</p>",
                }
            )
