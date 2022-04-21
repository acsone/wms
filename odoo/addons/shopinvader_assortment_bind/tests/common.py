# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.component.tests.common import SavepointComponentCase


class TestProductExport(SavepointComponentCase):
    @classmethod
    def setUpClass(cls):
        super(TestProductExport, cls).setUpClass()

        new_context = dict(tracking_disable=True, bind_products_immediately=True)
        cls.env = cls.env(context=dict(cls.env.context, **new_context))

        cls.product_template_in = cls.env["product.template"].create({"name": "P"})
        cls.product_in = cls.product_template_in.product_variant_id

        cls.product_template_out = cls.env["product.template"].create({"name": "N"})
        cls.product_out = cls.product_template_out.product_variant_id

        cls.product_templates = cls.product_template_in + cls.product_template_out
        cls.products = cls.product_in + cls.product_out

        cls.backend = cls.env.ref("shopinvader.backend_1")
        cls.backend.product_manual_binding = False

        vals_assortment = {
            "domain": "[('name', '=', 'P')]",
            "model_id": "product.product",
            "name": "assortment",
        }
        cls.assortment = cls.env["ir.filters"].create(vals_assortment)
        cls.backend.product_assortment_id = cls.assortment
