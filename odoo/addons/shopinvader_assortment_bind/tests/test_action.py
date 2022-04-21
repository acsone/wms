# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .common import TestProductExport


class TestProductExportFlow(TestProductExport):
    def test_template(self):
        self.product_templates.shopinvader_assortment_binding()
        self.assertTrue(self.product_in.shopinvader_bind_ids)
        self.assertFalse(self.product_out.shopinvader_bind_ids)

    def test_product(self):
        self.products.shopinvader_assortment_binding()
        self.assertTrue(self.product_in.shopinvader_bind_ids)
        self.assertFalse(self.product_out.shopinvader_bind_ids)

    def test_unbind_product(self):
        # given
        product_command = [(6, 0, self.product_out.ids)]
        vals = {"backend_id": self.backend.id, "product_ids": product_command}
        wizard_model = self.env["shopinvader.variant.binding.wizard"]
        wizard_model.create(vals).bind_products()
        self.assertTrue(self.product_out.shopinvader_bind_ids.active)
        # when
        self.products.shopinvader_assortment_binding()
        # then
        self.assertFalse(self.product_out.shopinvader_bind_ids.active)
