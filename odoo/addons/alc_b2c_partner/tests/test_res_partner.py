# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase

from ..models.res_partner import B2C_CUSTOMER_CATEGORY_REF


class TestResPartner(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_model = cls.env["res.partner"]
        cls.bc2_category = cls.env.ref(B2C_CUSTOMER_CATEGORY_REF)
        cls.partner = cls.partner_model.create({"name": "my test partner"})

    def test_00(self):
        """
        Data:

            partner without category
        Test case:
            set is_bc2_customer
            unset is_b2c_customer
        Expected result
            b2c category must be set on the partner
            b2c category must be removed from the partner
        """
        self.assertFalse(self.partner.category_id)
        self.partner.is_b2c_customer = True
        self.assertEqual(self.partner.category_id, self.bc2_category)
        self.partner.is_b2c_customer = False
        self.assertFalse(self.partner.category_id)

    def test_01(self):
        """
        Data:

            partner without category
        Test case:
            add b2c_category
            remove b2c_category
        Expected result
            is_b2c_customer is True
            is_b2c_customer is False
        """
        self.assertFalse(self.partner.is_b2c_customer)
        self.partner.write({"category_id": [Command.link(self.bc2_category.id)]})
        self.assertTrue(self.partner.is_b2c_customer)
        self.partner.write({"category_id": [Command.unlink(self.bc2_category.id)]})
        self.assertFalse(self.partner.is_b2c_customer)

    def test_02(self):
        """
        Data:

            partner without category
        Test case:
            set manual_sale_order_allowed
            set is_bc2_customer
            set manual_sale_order_allowed
        Expected result
            manual_sale_order_allowed is True
            manual_sale_order_allowed is False
            ValidationError
        """
        self.partner.manual_sale_order_allowed = True
        self.assertTrue(self.partner.manual_sale_order_allowed)
        self.partner.is_b2c_customer = True
        self.assertFalse(self.partner.manual_sale_order_allowed)
        with self.assertRaises(ValidationError):
            self.partner.manual_sale_order_allowed = True

    def test_03(self):
        """
        Data:

            partner without category
        Test case:
            set manual_sale_order_allowed
            add b2c_category
            set manual_sale_order_allowed
        Expected result
            manual_sale_order_allowed is True
            manual_sale_order_allowed is False
            ValidationError
        """
        self.partner.manual_sale_order_allowed = True
        self.assertTrue(self.partner.manual_sale_order_allowed)
        self.partner.category_id += self.bc2_category
        self.assertFalse(self.partner.manual_sale_order_allowed)
        with self.assertRaises(ValidationError):
            self.partner.manual_sale_order_allowed = True
