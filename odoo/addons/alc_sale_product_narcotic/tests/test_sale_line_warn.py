# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestSaleSaleLineWarn(TransactionCase):
    def test_sale_line_warn(self):
        categ_narco_reg = self.env.ref(
            "alc_product_category_data.product_categ_stupefiant"
        )
        narcotic = self.env["product.product"].create(
            {"name": "test narcotic 1", "categ_id": categ_narco_reg.id}
        )
        narcotic.product_tmpl_id._compute_sale_line_warn()

        self.assertEqual("warning", narcotic.sale_line_warn)
        self.assertTrue(narcotic.sale_line_warn_msg)

        no_narco = self.env["product.product"].create({"name": "no-narco"})
        self.assertEqual("no-message", no_narco.sale_line_warn)
        no_narco.sale_line_warn = "warning"
        no_narco.sale_line_warn_msg = "test warning"
