# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import timedelta

from odoo.fields import Date
from odoo.tests.common import Form, TransactionCase


class TestProductSupplierinfoDefaultPrice(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sinfo_model = cls.env["product.supplierinfo"]
        cls.product = cls.env["product.template"].create(
            {"name": "Virtual Home Staging"}
        )
        cls.partner_1 = cls.env["res.partner"].create({"name": "partner 1"})
        cls.partner_2 = cls.env["res.partner"].create({"name": "partner 2"})
        cls.sinfo_model.create(
            [
                {
                    "partner_id": cls.partner_1.id,
                    "product_tmpl_id": cls.product.id,
                    "price": 99,
                },
                {
                    "partner_id": cls.partner_1.id,
                    "product_tmpl_id": cls.product.id,
                    "price": 200,
                    "date_start": Date.today(),
                    "date_end": Date.today() + timedelta(days=30),
                },
            ],
        )

    def test_default_price_at_creation(self):
        line = self.sinfo_model.create(
            {"partner_id": self.partner_1.id, "product_tmpl_id": self.product.id}
        )
        self.assertEqual(line.price, 99)
        line_2 = self.sinfo_model.create(
            {"partner_id": self.partner_2.id, "product_tmpl_id": self.product.id}
        )
        self.assertEqual(line_2.price, 0)

    def test_default_price_at_change(self):
        sinfo_form = Form(self.sinfo_model.with_context(visible_product_tmpl_id=False))
        sinfo_form.product_tmpl_id = self.product
        sinfo_form.partner_id = self.partner_1
        self.assertEqual(sinfo_form.price, 99)

    def test_default_price_at_change_2(self):
        sinfo_form = Form(self.sinfo_model.with_context(visible_product_tmpl_id=False))
        sinfo_form.product_tmpl_id = self.product
        sinfo_form.partner_id = self.partner_2
        self.assertEqual(sinfo_form.price, 0)
