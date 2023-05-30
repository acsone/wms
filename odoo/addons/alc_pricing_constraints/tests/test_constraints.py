# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command
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

    def test_cannot_create_min_qty_on_anything_but_product(self):
        # this is OK:
        vals = self._get_item_vals(
            self.pricelist_discount,
            applied_on="1_product",
            product_tmpl_id=self.product_template.id,
            min_quantity=2,
        )
        item = self.env["product.pricelist.item"].create(vals)
        self.assertTrue(item)

        # cannot create a global item with a minimum quantity
        vals = self._get_item_vals(self.pricelist_discount, min_quantity=2)
        with self.assertRaises(ValidationError):
            self.env["product.pricelist.item"].create(vals)

        # creating on a variant is also bad
        vals["applied_on"] = "0_product_variant"
        vals["product_id"] = self.product.id
        with self.assertRaises(ValidationError):
            self.env["product.pricelist.item"].create(vals)

    def test_pricelist_creation(self):
        pricelist = self.env["product.pricelist"].create(
            {
                "name": "pricelist",
                "item_ids": [
                    (0, 0, {"compute_price": "percentage", "percent_price": 0}),
                    Command.create(
                        {
                            "compute_price": "formula",
                            "price_surcharge": 0,
                            "price_discount": 0,
                        }
                    ),
                ],
            }
        )
        self.assertFalse(pricelist.item_ids)
