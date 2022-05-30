# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.shopinvader_search_engine_update_product.tests.common import (
    TestProductUpdate,
)


class TestProductExportFlow(TestProductUpdate):
    def test_flow(self):
        # given
        vals = {
            "name": "Test VT Group",
            "product_template_ids": [(6, 0, [self.product_template.id])],
        }
        # when
        vt_group = self.env["veterinary.group"].create(vals)
        # then
        self.assertTrue(self.binding.to_update)

        # given
        self.binding.to_update = False
        partner = self.env["res.partner"].create({"name": "P"})
        # when  # just modifying the partner does not mark products to update
        vt_group.partner_ids = partner
        # then
        self.assertFalse(self.binding.to_update)

        # when
        vt_group.product_template_ids = [(5, 0, 0)]
        # then: if we removed the product, it is updated
        self.assertTrue(self.binding.to_update)

        # given: we add it back in to test unlink
        vt_group.product_template_ids = [(4, self.product_template.id, 0)]
        self.binding.to_update = False
        # when
        vt_group.unlink()
        # then
        self.assertTrue(self.binding.to_update)
