# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import random
import string

from odoo.exceptions import MissingError, ValidationError

from .common import CommonCase

ISO_DT_WITH_TZ = "2020-05-28T13:45:47+02:00"


class TestSalesService(CommonCase):
    @classmethod
    def setUpClass(cls):
        super(TestSalesService, cls).setUpClass()
        cls.pricelist_id = cls.env.ref(
            "alc_chronovet_connector.product_pricelist_chronovet"
        )
        # create a chronovet_partner
        cls.chronovet_partner = cls.env["res.partner"].create(
            {
                "name": "EXISTING CHRONOVET PARTNER",
                "category_id": [
                    (
                        4,
                        cls.env.ref(
                            "alc_chronovet_connector.res_partner_category_chronovet_customer"
                        ).id,
                    )
                ],
                "alcyon_category_id": cls.env.ref(
                    "specific_partner.partner_category_student"
                ).id,
                "ref": "CHRONOVET_ABC",
                "email": "chronovet@chronovet.be",
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
            }
        )

        # create a chronovet sale_order
        cls.chronovet_order = cls.env["sale.order"].create(
            {
                "chronovet_ref": "SO1",
                "partner_id": cls.chronovet_partner.id,
                "partner_invoice_id": cls.vt_partner.id,
                "partner_shipping_id": cls.vt_partner.id,
                "pricelist_id": cls.pricelist_id.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "chronovet_ref": "SOL1",
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
            1 existing SO
        Test case:
            Get order info with the chronovet ref
        Expected result:
            The so info
        """
        res = self.sales_service.dispatch("get", _id="SO1")
        self.assertTrue(res)
        self.assertEqual(res["state"], self.chronovet_order.state)
        self.assertEqual(res["ref"], self.chronovet_order.name)
        self.assertEqual(res["id"], "SO1")
        self.assertFalse(res["confirmation_date"])

    def test_01(self):
        """
        Test case:
            Get order info with an unknown chronovet ref
        Expected result:
            Missing error is raised
        """
        with self.assertRaises(MissingError):
            self.sales_service.dispatch("get", _id="UNKNOWN")

    def test_02(self):
        """
        Data:
            1 existing SO
        Test case:
            Search order info with the chronovet ref
        Expected result:
            The so info
        """
        res = self.sales_service.dispatch("search", params={"ids": ["SO1"]})
        self.assertEqual(res["size"], 1)
        result = res["data"][0]
        self.assertEqual(result["state"], self.chronovet_order.state)
        self.assertEqual(result["ref"], self.chronovet_order.name)
        self.assertEqual(result["id"], "SO1")
        self.assertFalse(result["confirmation_date"])

    def test_03(self):
        """
        Test case:
            Search order info with the unknown chronovet ref
        Expected result:
            Empty result
        """
        res = self.sales_service.dispatch("search", params={"ids": ["UNKNOWN"]})
        self.assertEqual(res["size"], 0)
        self.assertFalse(res["data"])

    def test_04(self):
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
        """
        recipient_info = self._gen_recipent()
        params = {
            "id": "SO2",
            "customer_ref": self.vt_partner.ref,
            "date": ISO_DT_WITH_TZ,
            "recipient": recipient_info,
            "lines": [
                {
                    "line_id": "SOL2",
                    "sku": self.saleable_product.default_code,
                    "quantity": 10,
                }
            ],
        }
        res = self.sales_service.dispatch("create", params=params)
        self.assertTrue(res)
        new_so = self._get_so_from_name(res["ref"])
        self.assertTrue(new_so)
        self.assertEqual(new_so.partner_id.ref, "CHRONOVET_%s" % recipient_info["id"])
        self.assertEqual(new_so.partner_invoice_id, self.vt_partner)
        self.assertEqual(new_so.partner_shipping_id, self.vt_partner)
        self.assertEqual(new_so.date_order, "2020-05-28 11:45:47")
        self.assertTrue(self.chronovet_backend.pricelist_id)
        self.assertEqual(new_so.pricelist_id, self.chronovet_backend.pricelist_id)
        self.assertTrue(self.chronovet_backend.sale_team_id)
        self.assertEqual(new_so.team_id, self.chronovet_backend.sale_team_id)
        self.assertTrue(self.chronovet_backend.payment_mode_id)
        self.assertEqual(new_so.payment_mode_id, self.chronovet_backend.payment_mode_id)
        self.assertEqual(1, len(new_so.order_line))
        sol = new_so.order_line
        self.assertEqual(sol.product_id, self.saleable_product)
        self.assertEqual(sol.price_unit, 8.8)  # 10 - 12%
        self.assertEqual(sol.product_qty, 10)

    def test_05(self):
        """
        Test case:
            Create a new SO with a wrong customer_ref (veterinary)
        Expected result:
            ValidationError must be raised
        """
        recipient_info = self._gen_recipent()
        params = {
            "id": "SO2",
            "customer_ref": "unknow",
            "date": ISO_DT_WITH_TZ,
            "recipient": recipient_info,
            "lines": [
                {
                    "line_id": "SOL2",
                    "sku": self.saleable_product.default_code,
                    "quantity": 10,
                }
            ],
        }
        with self.assertRaises(ValidationError):
            self.sales_service.dispatch("create", params=params)

    def test_06(self):
        """
        Data:
            An existing veterinary
            An existing partner referenced into the request
        Test case:
            Create a new SO for a new partner and the existing veterinary
        Expected result:
            A new SO is created with:
                partner -> the existing partner
                shipping partner -> the veterinary
                invoice partner -> the veterinary
        """
        recipient_info = self._gen_recipent()
        recipient_info["id"] = "ABC"
        params = {
            "id": "SO2",
            "customer_ref": self.vt_partner.ref,
            "date": ISO_DT_WITH_TZ,
            "recipient": recipient_info,
            "lines": [
                {
                    "line_id": "SOL2",
                    "sku": self.saleable_product.default_code,
                    "quantity": 10,
                }
            ],
        }
        res = self.sales_service.dispatch("create", params=params)
        self.assertTrue(res)
        new_so = self._get_so_from_name(res["ref"])
        self.assertTrue(new_so)
        self.assertEqual(new_so.partner_id, self.chronovet_partner)
        self.assertEqual(new_so.partner_invoice_id, self.vt_partner)
        self.assertEqual(new_so.partner_shipping_id, self.vt_partner)

    def test_07(self):
        """
        Test case:
            Create a new SO with a wrong product ref
        Expected result:
            ValidationError must be raised
        """
        recipient_info = self._gen_recipent()
        params = {
            "id": "SO2",
            "customer_ref": self.vt_partner.ref,
            "date": ISO_DT_WITH_TZ,
            "recipient": recipient_info,
            "lines": [{"line_id": "SOL2", "sku": "????", "quantity": 10}],
        }
        with self.assertRaises(ValidationError):
            self.sales_service.dispatch("create", params=params)

    def test_08(self):
        """
        Test case:
            Create a new SO with a product ref not into the assortment
        Expected result:
            ValidationError must be raised
        """
        recipient_info = self._gen_recipent()
        params = {
            "id": "SO2",
            "customer_ref": self.vt_partner.ref,
            "date": ISO_DT_WITH_TZ,
            "recipient": recipient_info,
            "lines": [
                {
                    "line_id": "SOL2",
                    "sku": self.not_saleable_product.default_code,
                    "quantity": 10,
                }
            ],
        }
        with self.assertRaises(ValidationError):
            self.sales_service.dispatch("create", params=params)
