# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader.tests.common import CommonCase


class TestShopinvaderUrlocales(CommonCase):
    @classmethod
    def setUpClass(cls):
        super(TestShopinvaderUrlocales, cls).setUpClass()
        cls.product_exporter = cls.env.ref("shopinvader.ir_exp_shopinvader_variant")
        cls.category_exporter = cls.env.ref("shopinvader.ir_exp_shopinvader_category")
        lang = cls._install_lang("base.lang_fr")
        cls.backend.lang_ids |= lang
        cls.backend.bind_all_category()
        cls.variant = cls.env.ref("product.product_product_4b")
        cls._bind_products(cls.variant)

    @classmethod
    def _bind_products(cls, products, backend=None):
        # TO BE REMOVED. REDEFINED FROM shopinvader since the original one
        # is not a classmethod
        backend = backend or cls.backend
        bind_wizard_model = cls.env["shopinvader.variant.binding.wizard"]
        bind_wizard = bind_wizard_model.create(
            {
                "backend_id": backend.id,
                "product_ids": [(6, 0, products.ids)],
                "run_immediately": True,
            }
        )
        bind_wizard.bind_products()

    def _test_url_key_locales(self, bindings, exporter, expected):
        for binding in bindings:
            url_key_locals = binding.url_key_locales
            for lang, url in expected.items():
                self.assertIn(lang, url_key_locals)
                self.assertIn(url, url_key_locals[lang])
            json = binding.jsonify(exporter.get_json_parser(), one=True)
            self.assertIn("url_key_locales", json)
            self.assertDictEqual(json["url_key_locales"], url_key_locals)

    def test_product_url_key_locales(self):
        expected = {
            "en_US": u"ipad-retina-display",
            "fr_FR": u"ipad-avec-ecran-retina",
        }
        exporter = self.product_exporter
        bindings = self.variant.shopinvader_bind_ids
        self._test_url_key_locales(bindings, exporter, expected)

    def test_category_url_key_locales(self):
        categ = self.env.ref("product.product_category_1")
        expected = {
            "en_US": u"all/saleable",
            "fr_FR": u"tous/en-vente",
        }
        exporter = self.category_exporter
        bindings = categ.shopinvader_bind_ids
        self._test_url_key_locales(bindings, exporter, expected)
