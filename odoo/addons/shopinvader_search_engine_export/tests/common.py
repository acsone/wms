# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.component.tests.common import SavepointComponentCase


class TestProductExport(SavepointComponentCase):
    @classmethod
    def setUpClass(cls):
        super(TestProductExport, cls).setUpClass()

        cls.product_template = cls.env["product.template"].create({"name": "P"})
        cls.product = cls.product_template.product_variant_id

        cls.backend = cls.env.ref("shopinvader.backend_1")
        cls.backend.bind_all_product(domain=[("id", "=", cls.product_template.id)])
