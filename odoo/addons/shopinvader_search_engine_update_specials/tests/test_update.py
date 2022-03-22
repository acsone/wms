# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from .common import TestProductSpecialUpdate


class TestProductExportFlow(TestProductSpecialUpdate):
    def test_flow(self):
        # given
        vals = {"product_template_id": self.product_template.id}
        # when
        special = self.env["product.discount.special"].create(vals)
        # then
        self.assertTrue(self.binding.to_update)

        # given
        self.binding.to_update = False
        # when
        special.date_start = self.today
        # then
        self.assertTrue(self.binding.to_update)

        # given
        self.binding.to_update = False
        # when
        special.unlink()
        # then
        self.assertTrue(self.binding.to_update)
