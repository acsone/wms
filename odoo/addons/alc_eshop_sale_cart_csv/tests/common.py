# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.sale_cart_rest_api.tests.common import TestSaleCartRestApiCase


class TestSaleCartRestApiCsvCase(TestSaleCartRestApiCase):
    @classmethod
    def setUpClass(cls):
        super(TestSaleCartRestApiCsvCase, cls).setUpClass()
        vals_product = {"name": "N", "default_code": "sku"}
        cls.product = cls.env["product.product"].create(vals_product)
