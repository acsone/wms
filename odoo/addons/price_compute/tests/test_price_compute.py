# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from .common import PriceComputeCase


class TestPriceCompute(PriceComputeCase):
    def test_product_rule(self):
        item = self.pricelist_item_product_rule._get_rule(
            self.p1, fields.Date.today(self)
        )
        self.assertTrue(item)
        self.assertEqual(item.product_id, self.p1)
        item = self.pricelist_item_category_rule._get_rule(
            self.p1, fields.Date.today(self)
        )
        self.assertFalse(item)

    def test_category_rule(self):
        item = self.pricelist_item_category_rule._get_rule(
            self.p2, fields.Date.today(self)
        )
        self.assertTrue(item)
        self.assertEqual(item.categ_id, self.p2.categ_id.parent_id)
        item = self.pricelist_item_product_rule._get_rule(
            self.p2, fields.Date.today(self)
        )
        self.assertFalse(item)
