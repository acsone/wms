# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from vcr_unittest import VCRTestCase

from odoo.tests.common import TransactionCase


class TestProduct(VCRTestCase, TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.lang = (
            cls.env["res.lang"]
            .with_context(active_test=False)
            .search([("code", "=", "fr_FR")])
        )
        cls.env["res.lang"]._activate_lang("fr_FR")
        cls.env["ir.module.module"]._load_module_terms(["base"], ["fr_FR"])

    def test_flow(self):
        vals_product = {"name": "P", "link_info": "not_a_link", "type": "consu"}
        product = self.env["product.template"].create(vals_product)
        self.assertEqual(product.links_offline, "link_info")

        product.link_info = "https://www.duckduckgo.com/"
        self.assertFalse(product.links_offline)

        product.link_notice = "also_not_a_link"
        self.assertEqual(product.links_offline, "link_notice")

        product.link_notice = "https://www.google.be/"
        self.assertFalse(product.links_offline)

        product_fr = product.with_context(lang=self.lang.code)
        product_fr.link_info = "pas_un_lien"
        self.assertEqual(product.links_offline, "link_info_fr_FR")
