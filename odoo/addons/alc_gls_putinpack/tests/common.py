# coding: utf-8
# Copyright 2021 ACSONE SA/NV.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.delivery_carrier_label_gls.tests.common import TestGLS


class TestGLSWizard(TestGLS):
    @classmethod
    def setUpClass(cls):
        super(TestGLSWizard, cls).setUpClass()

        vals_product_2 = {"name": "product2", "type": "product", "weight": 1}
        cls.product_2 = cls.env["product.product"].create(vals_product_2)
        vals_order_line_2 = {
            "name": "Line Description",
            "order_id": cls.sale_order.id,
            "product_id": cls.product_2.id,
        }
        cls.order_line_2 = cls.env["sale.order.line"].create(vals_order_line_2)
