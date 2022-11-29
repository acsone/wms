# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.sale_cart_rest_api.tests.common import TestSaleCartRestApiCase


class TestSaleCartRestApiPharmacy(TestSaleCartRestApiCase):
    @classmethod
    def setUpClass(cls):
        super(TestSaleCartRestApiPharmacy, cls).setUpClass()

        cls.category_human = cls.env.ref("specific_data.product_categ_humain")
        vals_product_human = {"name": "Human", "categ_id": cls.category_human.id}
        cls.product_human = cls.env["product.product"].create(vals_product_human)
