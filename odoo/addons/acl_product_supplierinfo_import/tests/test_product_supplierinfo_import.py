# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from odoo.tests.common import Form, TransactionCase


class TestProductSupplierInfoImport(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env.ref("base.res_partner_4")
        cls.product_tmpl = cls.env.ref("product.product_product_6_product_template")
        cls.product = cls.env.ref("product.product_product_6")
        cls.product_tmpl.cnk_code = "product_cnk_code"
        cls.supplierinfo = cls.env.ref("product.product_supplierinfo_2")
        cls.supplierinfo.search([("id", "!=", cls.supplierinfo.id)]).unlink()
        cls.supplierinfo.product_code = "product code"

    def test_00(self):
        """Create supplierinfo with product_code."""
        supplierinfo = self.supplierinfo.create(
            {
                "product_code": "product code",
                "partner_id": self.partner.id,
                "date_start": datetime.today(),
                "date_end": datetime.today() + timedelta(days=1),
            }
        )
        self.assertEqual(supplierinfo.product_tmpl_id, self.product_tmpl)

    def test_01(self):
        """Create supplierinfo with product_cnk_code."""
        supplierinfo = self.supplierinfo.create(
            {
                "product_cnk_code": "product_cnk_code",
                "partner_id": self.partner.id,
                "date_start": datetime.today(),
                "date_end": datetime.today() + timedelta(days=1),
            }
        )
        self.assertEqual(supplierinfo.product_tmpl_id, self.product_tmpl)
        self.assertEqual(supplierinfo.product_code, "product code")

    def test_02(self):
        """Test product_code change at product change."""
        supplierinfo_form = Form(self.env["product.supplierinfo"])
        supplierinfo_form.partner_id = self.partner
        self.assertFalse(supplierinfo_form.product_code)
        supplierinfo_form.product_id = self.product
        self.assertEqual(supplierinfo_form.product_code, "product code")
