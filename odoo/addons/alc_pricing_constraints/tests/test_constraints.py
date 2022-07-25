# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError

from .common import TestConstraints


class TestConstraintsFlow(TestConstraints):
    def test_cannot_create_discount_based_on_cost(self):
        pl = self.pricelist_discount
        vals = self._get_item_vals(pl, compute_price="formula", base="standard_price")
        with self.assertRaises(ValidationError):
            self.env["product.pricelist.item"].create(vals)

    def test_cannot_create_discount_based_on_other_pricelist(self):
        pl = self.pricelist_discount
        vals = self._get_item_vals(pl, compute_price="formula", base="pricelist")
        with self.assertRaises(ValidationError):
            self.env["product.pricelist.item"].create(vals)

    def test_cannot_create_0_percent_discount(self):
        vals = self._get_item_vals(
            self.pricelist_discount, compute_price="percentage", percent_price=0
        )
        with self.assertRaises(ValidationError):
            self.env["product.pricelist.item"].create(vals)

    def test_can_create_10_percent_discount(self):
        vals = self._get_item_vals(
            self.pricelist_discount, compute_price="percentage", percent_price=10
        )
        item = self.env["product.pricelist.item"].create(vals)
        self.assertTrue(item)

    def test_cannot_create_useless_formula(self):
        vals = self._get_item_vals(
            self.pricelist_discount,
            compute_price="formula",
            price_surcharge=0,
            price_discount=0,
        )
        with self.assertRaises(ValidationError):
            self.env["product.pricelist.item"].create(vals)

    def test_can_create_useful_formula(self):
        vals = self._get_item_vals(
            self.pricelist_base,
            compute_price="formula",
            price_surcharge=10,
            price_discount=0,
        )
        item = self.env["product.pricelist.item"].create(vals)
        self.assertTrue(item)

        vals = self._get_item_vals(
            self.pricelist_base,
            compute_price="formula",
            price_surcharge=0,
            price_discount=10,
        )
        item = self.env["product.pricelist.item"].create(vals)
        self.assertTrue(item)
