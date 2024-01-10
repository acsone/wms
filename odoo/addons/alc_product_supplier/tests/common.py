# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestProductTemplateCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_tmpl_model = cls.env["product.template"]
        cls.sinfo_model = cls.env["product.supplierinfo"]
        cls.supplier = cls.env["res.partner"].create({"name": "supplier"})
        cls.product_no_seller = cls.product_tmpl_model.create({"name": "no seller"})
        cls.product_seller = cls.product_tmpl_model.create(
            {"name": "with seller", "default_code": "1234"}
        )
        cls.supplierinfo = cls.sinfo_model.create(
            {
                "partner_id": cls.supplier.id,
                "product_code": "ABCD",
                "product_tmpl_id": cls.product_seller.id,
            }
        )
