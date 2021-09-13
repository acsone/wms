# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestProduct(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestProduct, cls).setUpClass()

        Langs = cls.env["res.lang"].with_context(active_test=False)
        cls.lang = Langs.search([("code", "=", "fr_FR")])
        cls.lang.active = True
        cls.env["ir.translation"].load_module_terms(["base"], [cls.lang.code])

    def test_flow(self):
        vals_product = {"name": "P", "link_info": "not_a_link", "type": "consu"}
        product = self.env["product.template"].create(vals_product)
        self.assertEqual(product.links_offline, "link_info")

        product.link_info = "https://www.acsone.eu/"  # should be online, right?
        self.assertFalse(product.links_offline)

        product.link_notice = "also_not_a_link"
        self.assertEqual(product.links_offline, "link_notice")

        product.link_notice = "https://www.google.be/"
        self.assertFalse(product.links_offline)

        product_fr = product.with_context(lang=self.lang.code)
        product_fr.link_info = "pas_un_lien"
        self.assertEqual(product.links_offline, "link_info_fr_FR")
