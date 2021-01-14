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
        # create a b2c_partner
        cls.discount_pricelist_id = cls.env.ref(
            "alc_b2c_connector.product_pricelist_b2c"
        )
        cls.discount_pricelist_id.currency_id = cls.currency_id
        cls.b2c_backend.discount_pricelist_id = cls.discount_pricelist_id
        cls.b2c_partner = cls.env["res.partner"].create(
            {
                "name": "EXISTING B2C PARTNER",
                "is_b2c_customer": True,
                "alcyon_category_id": cls.env.ref(
                    "specific_partner.partner_category_student"
                ).id,
                "ref": "%s_ABC" % cls.b2c_backend.sale_channel,
                "email": "b2c@b2c.be",
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
                "supplier_promotion_sale_allowed": True,
            }
        )

        # create a b2c sale_order
        cls.b2c_order = cls.env["sale.order"].create(
            {
                "b2c_ref": 10,
                "partner_id": cls.b2c_partner.id,
                "partner_invoice_id": cls.vt_partner.id,
                "partner_shipping_id": cls.vt_partner.id,
                "pricelist_id": cls.pricelist_id.id,
                "discount_pricelist_id": cls.discount_pricelist_id.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "b2c_ref": 1,
                            "product_id": cls.saleable_product.id,
                            "name": cls.saleable_product.name,
                            "product_uom": cls.saleable_product.uom_id.id,
                            "product_uom_qty": 10,
                        },
                    )
                ],
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

    def test_01(self):
        """
        Data:
            An existing veterinary
        Test case:
            Create a new SO for a new partner and the existing veterinary
        Expected result:
            A new partner is created
            A new SO is created with:
                partner -> new partner
                shipping partner -> the veterinary
                invoice partner -> the veterinary
                priclist -> the one from the backend
                payment_mode -> the one from the backend
                payment_term_id -> the one from the backend
                supplier_promotion_allowed -> the one from the veterinary
        """
        recipient_info = self._gen_recipent()
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
        self.assertEqual(
            new_so.partner_id.ref,
            "{}_{}".format(self.b2c_backend.sale_channel, recipient_info["id"]),
        )
        self.assertEqual(new_so.partner_invoice_id, self.vt_partner)
        self.assertEqual(new_so.partner_shipping_id, self.vt_partner)
        self.assertFalse(new_so.partner_id.is_sale_back_order_accepted)
        self.assertEqual(new_so.date_order, "2020-05-28 11:45:47")
        self.assertTrue(self.b2c_backend.pricelist_id)
        self.assertEqual(new_so.pricelist_id, self.b2c_backend.pricelist_id)
        self.assertTrue(self.b2c_backend.sale_team_id)
        self.assertEqual(new_so.team_id, self.b2c_backend.sale_team_id)
        self.assertTrue(self.b2c_backend.payment_mode_id)
        self.assertEqual(new_so.payment_mode_id, self.b2c_backend.payment_mode_id)
        self.assertEqual(self.b2c_backend.payment_term_id, self.payment_term_test)
        self.assertEqual(new_so.payment_term_id, self.payment_term_test)
        self.assertTrue(new_so.supplier_promotion_allowed)
        self.assertEqual(1, len(new_so.order_line))
        sol = new_so.order_line
        self.assertEqual(sol.product_id, self.saleable_product)
        self.assertEqual(sol.discount3, 12)  # discount in %
        self.assertEqual(sol.price_unit, 10)
        self.assertEqual(sol.product_qty, 10)
