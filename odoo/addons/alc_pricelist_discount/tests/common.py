# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestPricelistDiscount(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestPricelistDiscount, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.parameter_model = cls.env["ir.config_parameter"]
        cls.parameter_model.set_param("constrain_discount_pricelist", "1")

        cls.pricelist_model = cls.env["product.pricelist"]
        vals_pricelist_base = {"name": "Base", "is_discount": False}
        cls.pricelist_base = cls.pricelist_model.create(vals_pricelist_base)
        vals_pricelist_discount = {"name": "Discount", "is_discount": True}
        cls.pricelist_discount = cls.pricelist_model.create(vals_pricelist_discount)

        cls.partner = cls.env["res.partner"].create({"name": "P"})
