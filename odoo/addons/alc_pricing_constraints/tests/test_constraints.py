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

    def test_cannot_create_formula_based_on_pricelist(self):
        vals = self._get_item_vals(
            self.pricelist_discount,
            compute_price="formula",
            base="pricelist",
            base_pricelist_id=self.pricelist_base.id,
        )
        with self.assertRaises(ValidationError):
            self.env["product.pricelist.item"].create(vals)
