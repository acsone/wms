# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import random
import string

from odoo.addons.alc_b2c_connector.tests.common import CommonCase

ISO_DT_WITH_TZ = "2020-05-28T13:45:47+02:00"


class TestSalesService(CommonCase):
    @classmethod
    def setUpClass(cls):
        super(TestSalesService, cls).setUpClass()
        cls.pricelist_id = cls.env.ref("alc_b2c_connector.product_pricelist_b2c")
        # create a b2c_partner
        cls.b2c_partner = cls.env["res.partner"].create(
            {
                "name": "EXISTING B2C PARTNER",
                "is_b2c_customer": True,
                "alcyon_category_id": cls.env.ref(
                    "specific_partner.partner_category_student"
                ).id,
                "ref": "%s_ABC" % cls.b2c_backend.sale_channel,
                "email": "b2c@b2c.be",
                "discount_pricelist_id": cls.pricelist_id.id,
                "supplier_promotion_sale_allowed": True,
            }
        )

        # create a vete
        cls.vt_partner = cls.env["res.partner"].create(
            {
                "name": "VT",
                "alcyon_category_id": cls.env.ref(
                    "specific_partner.partner_category_veterinary"
                ).id,
                "ref": "VTREF",
                "email": "vt@vt.be",
                "discount_pricelist_id": cls.pricelist_id.id,
                "supplier_promotion_sale_allowed": True,
            }
        )

        cls.SaleOrder = cls.env["sale.order"]
        cls.payment_term_test = cls.env.ref(
            "account.account_payment_term_advance"
        ).copy()
        cls.b2c_backend.payment_term_id = cls.payment_term_test

        with cls.work_on_services() as work:
            cls.sales_service = work.component(usage="sales")

    @classmethod
    def _gen_string(cls, length=10):
        return "".join(random.choice(string.ascii_letters) for _ in range(length))

    @classmethod
    def _gen_recipent(cls, _id=None, title="mr"):
        _id = _id or cls._gen_string()
        return {
            "id": _id,
            "title": title,
            "last_name": cls._gen_string(),
            "first_name": cls._gen_string(),
            "street": cls._gen_string(),
            "street2": cls._gen_string(),
            "zip": cls._gen_string(),
            "city": cls._gen_string(),
            "email": cls._gen_string(),
            "phone": cls._gen_string(),
            "mobile": cls._gen_string(),
        }

    def _get_so_from_name(self, name):
        return self.SaleOrder.search([("name", "=", name)])

    def test_00(self):
        """
        Data:
            An existing veterinary with a
            discount_pricelist and supplier_promotion_allowed=True
            A new customer
        Test case:
            Create a new SO for a new partner and the existing veterinary
        Expected result:
            A new SO is created with:
                discount_pricelist_id False
                supplier_promotion_allowed False
        """
        recipient_info = self._gen_recipent()
        recipient_info["id"] = "ABC"
        params = {
            "id": 2,
            "customer_ref": self.vt_partner.ref,
            "date": ISO_DT_WITH_TZ,
            "recipient": recipient_info,
            "lines": [
                {
                    "line_id": 2,
                    "sku": self.saleable_product.default_code,
                    "quantity": 10,
                }
            ],
        }
        res = self.sales_service.dispatch("create", params=params)
        self.assertTrue(res)
        new_so = self._get_so_from_name(res["ref"])
        self.assertTrue(new_so)
        self.assertFalse(new_so.discount_pricelist_id)
        self.assertFalse(new_so.supplier_promotion_allowed)

    def test_01(self):
        """
        Data:
            An existing veterinary with a
            discount_pricelist and supplier_promotion_allowed=True
            A n existing customer with a
            discount_pricelist and supplier_promotion_allowed=True
        Test case:
            Create a new SO for a new partner and the existing veterinary
        Expected result:
            A new SO is created with:
                discount_pricelist_id False
                supplier_promotion_allowed False
        """
        recipient_info = self._gen_recipent()
        recipient_info["id"] = "%s_ABC" % self.b2c_backend.sale_channel
        params = {
            "id": 2,
            "customer_ref": self.vt_partner.ref,
            "date": ISO_DT_WITH_TZ,
            "recipient": recipient_info,
            "lines": [
                {
                    "line_id": 2,
                    "sku": self.saleable_product.default_code,
                    "quantity": 10,
                }
            ],
        }
        res = self.sales_service.dispatch("create", params=params)
        self.assertTrue(res)
        new_so = self._get_so_from_name(res["ref"])
        self.assertTrue(new_so)
        self.assertFalse(new_so.discount_pricelist_id)
        self.assertFalse(new_so.supplier_promotion_allowed)
