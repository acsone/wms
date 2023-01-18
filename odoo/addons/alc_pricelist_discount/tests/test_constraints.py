# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.exceptions import ValidationError

from .common import TestPricelistDiscountCommon


class TestPricelistDiscountConstraint(TestPricelistDiscountCommon):
    def test_can_update_unassigned_pricelist(self):
        """As long as a pricelist is not in use, it can be updated."""
        self.pricelist_discount.is_discount = False
        self.assertFalse(self.pricelist_discount.is_discount)

    def test_cannot_update_assigned_discount_pricelist(self):
        self.partner.discount_pricelist_ids = self.pricelist_discount

        with self.assertRaises(ValidationError):
            self.pricelist_discount.is_discount = False

    def test_cannot_assign_discount_pricelist_as_base(self):
        with self.assertRaises(ValidationError):
            self.partner.discount_pricelist_ids = self.pricelist_base

    def test_cannot_update_assigned_base_pricelist(self):
        self.partner.property_product_pricelist = self.pricelist_base

        with self.assertRaises(ValidationError):
            self.pricelist_base.is_discount = True

    def test_cannot_assign_base_pricelist_as_discount(self):
        with self.assertRaises(ValidationError):
            self.partner.property_product_pricelist = self.pricelist_discount

    def test_disable_constraints(self):
        """After having disabled the constraint, we can do whatever."""
        self.parameter_model.set_param("constrain_discount_pricelist", "0")
        self.partner.discount_pricelist_ids = self.pricelist_base  # would raise

        self.partner.discount_pricelist_ids = self.pricelist_discount
        self.pricelist_discount.is_discount = False  # would raise

        self.assertFalse(self.partner.discount_pricelist_ids.is_discount)
