# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.tests.common import TransactionCase


class TestSearchCnk(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.model_template = cls.env["product.template"]
        cls.model_product = cls.env["product.product"]
        cls.figeac = cls._create_product_template("1988 Petit Figeac", "0222642")
        cls.beaujolais = cls._create_product_template("2020 Beaujolais", "0666824")
        cls.emilion = cls._create_product_template("222 St Emilion", "0999135")

    @classmethod
    def _create_product_template(cls, name, cnk_code, **kwargs):
        return cls.model_template.create(dict(kwargs, name=name, cnk_code=cnk_code))
