# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
import random
import string

from odoo.exceptions import MissingError, ValidationError

from .common import CommonCase

ISO_DT_WITH_TZ = "2020-05-28T13:45:47+02:00"


class TestSalesService(CommonCase):
    @classmethod
    def setUpClass(cls):
        super(TestSalesService, cls).setUpClass()
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
            }
        )

        # create a specific payment mode for the VT
        cls.vt_payment_mode = cls.env["account.payment.mode"].create(
            {
                "name": "Specific VT payment mode",
                "company_id": cls.env.ref("base.main_company").id,
                "bank_account_link": "variable",
                "payment_method_id": cls.env.ref(
                    "account.account_payment_method_manual_in"
                ).id,
                "payment_type": "inbound",
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
                "customer_payment_mode_id": cls.vt_payment_mode.id,
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

    def _process_picking(self, picking):
        picking.force_assign()
        for pack in picking.pack_operation_product_ids:
            pack.qty_done = pack.product_qty
        picking.do_new_transfer()

    def _deliver_orders(self, orders):
        for order in orders:
            # validate SO
            order.action_confirm()
            # process deliveries
            picking_internals = order.picking_ids.filtered(
                lambda p: p.picking_type_code == "internal"
            )
            picking_outs = order.picking_ids.filtered(
                lambda p: p.picking_type_code == "outgoing"
            )
            for picking in picking_internals:
                self._process_picking(picking)
                self.assertEqual(picking.state, "done")
            for picking in picking_outs:
                self._process_picking(picking)
                self.assertEqual(picking.state, "done")

    def test_00(self):
        """
        Data:
            1 existing SO
        Test case:
            Get order info with the b2c ref
        Expected result:
            The so info
        """
        res = self.sales_service.dispatch("get", _id=10)
        self.assertTrue(res)
        self.assertEqual(res["state"], self.b2c_order.state)
        self.assertEqual(res["ref"], self.b2c_order.name)
        self.assertEqual(res["id"], 10)
        self.assertFalse(res["confirmation_date"])

    def test_01(self):
        """
        Test case:
            Get order info with an unknown b2c ref
        Expected result:
            Missing error is raised
        """
        with self.assertRaises(MissingError):
            self.sales_service.dispatch("get", _id=9999)

    def test_02(self):
        """
        Data:
            1 existing SO
        Test case:
            Search order info with the b2c ref
        Expected result:
            The so info
        """
        res = self.sales_service.dispatch("search", params={"ids": [10]})
        self.assertEqual(res["size"], 1)
        result = res["data"][0]
        self.assertEqual(result["state"], self.b2c_order.state)
        self.assertEqual(result["ref"], self.b2c_order.name)
        self.assertEqual(result["id"], 10)
        self.assertFalse(result["confirmation_date"])

    def test_03(self):
        """
        Test case:
            Search order info with the unknown b2c ref
        Expected result:
            Empty result
        """
        res = self.sales_service.dispatch("search", params={"ids": [9999]})
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
                payment_term_id -> the one from the backend
                supplier_promotion_allowed -> the one from the veterinary
                a new message with the json has been added into the chatter
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
            u"{}_{}".format(self.b2c_backend.sale_channel, recipient_info["id"]),
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
        self.assertEqual(sol.discount3, 0)  # discount in %
        self.assertEqual(sol.price_unit, 10)
        self.assertEqual(sol.product_qty, 10)
        self.assertIn(
            json.dumps(params, sort_keys=True),
            "\n".join(new_so.mapped("message_ids.body")),
        )

    def test_04_01(self):
        """
        Data:
            An existing veterinary with a specific payment_mode
            A backend without payment_mode
        Test case:
            Create a new SO for a new partner and the existing veterinary
        Expected result:
            A new SO is created with:
                payment_mode -> the one from the veterinary

        """
        self.b2c_backend.payment_mode_id = False
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
        self.assertEqual(new_so.payment_mode_id, self.vt_payment_mode)

    def test_04_02(self):
        """
        Data:
            A backend with a picking_policy
        Test case:
            1. Create a new SO for a new partner and the existing veterinary
            2. Change the picking_policy on the backend
            3. Create a new so
        Expected result:
            1. A new SO is created with:
                picking policy -> the one from the backend
            2. A new SO is created with:
                picking policy -> the one from the backend

        """
        for i, policy in enumerate(["one", "direct"]):
            self.b2c_backend.picking_policy = policy
            recipient_info = self._gen_recipent()
            params = {
                "id": i + 10,
                "customer_ref": self.vt_partner.ref,
                "date": ISO_DT_WITH_TZ,
                "recipient": recipient_info,
                "lines": [
                    {
                        "line_id": i + 10,
                        "sku": self.saleable_product.default_code,
                        "quantity": 10,
                    }
                ],
            }
            res = self.sales_service.dispatch("create", params=params)
            self.assertTrue(res)
            new_so = self._get_so_from_name(res["ref"])
            self.assertTrue(new_so)
            self.assertEqual(new_so.picking_policy, policy)

    def test_05(self):
        """
        Test case:
            Create a new SO with a wrong customer_ref (veterinary)
        Expected result:
            ValidationError must be raised
        """
        recipient_info = self._gen_recipent()
        params = {
            "id": 2,
            "customer_ref": "unknow",
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
        recipient_info = self._gen_recipent(title="mm")
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
        self.assertEqual(new_so.partner_id, self.b2c_partner)
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
            "id": 2,
            "customer_ref": self.vt_partner.ref,
            "date": ISO_DT_WITH_TZ,
            "recipient": recipient_info,
            "lines": [{"line_id": 2, "sku": "????", "quantity": 10}],
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
            "id": 2,
            "customer_ref": self.vt_partner.ref,
            "date": ISO_DT_WITH_TZ,
            "recipient": recipient_info,
            "lines": [
                {
                    "line_id": 2,
                    "sku": self.not_saleable_product.default_code,
                    "quantity": 10,
                }
            ],
        }
        with self.assertRaises(ValidationError):
            self.sales_service.dispatch("create", params=params)

    def test_09(self):
        """
        Test case:
            Create a new SO with 2 lines.
            5 saleable products are in stock
            110  saleable product2s are in stock
        Expected result:
            A new SO with 2 lines is created and confirmed
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
                },
                {
                    "line_id": 3,
                    "sku": self.saleable_product_2.default_code,
                    "quantity": 1,
                },
            ],
        }
        res = self.sales_service.dispatch("create", params=params)
        self.assertTrue(res)
        new_so = self._get_so_from_name(res["ref"])
        self.assertEqual(2, len(new_so.order_line))
        self.assertEqual("sale", new_so.state)
        res.pop("confirmation_date")
        self.assertDictEqual(
            {
                "id": 2,
                "lines": [
                    {
                        "line_id": 2,
                        "qty_backorder": 5,
                        "qty_cancelled": 0,
                        "qty_delivered": 0,
                        "qty_ordered": 10,
                        "qty_returned": 0,
                        "sku": u"12345",
                    },
                    {
                        "line_id": 3,
                        "qty_backorder": 0,
                        "qty_cancelled": 0,
                        "qty_delivered": 0,
                        "qty_ordered": 1,
                        "qty_returned": 0,
                        "sku": u"23456",
                    },
                ],
                "ref": new_so.name,
                "state": u"sale",
            },
            res,
        )

    def test_10(self):
        """
        Test case:
            1. Create a new SO with 2 lines.
               5 saleable products are in stock
               110  saleable product2s are in stock

            2. Deliver available product
        Expected result:
            1 state is 'sale'
            2 state is 'delivery'
        """
        recipient_info = self._gen_recipent()
        params = {
            "id": 99,
            "customer_ref": self.vt_partner.ref,
            "date": ISO_DT_WITH_TZ,
            "recipient": recipient_info,
            "lines": [
                {
                    "line_id": 2,
                    "sku": self.saleable_product.default_code,
                    "quantity": 10,
                },
                {
                    "line_id": 3,
                    "sku": self.saleable_product_2.default_code,
                    "quantity": 1,
                },
            ],
        }
        res = self.sales_service.dispatch("create", params=params)
        self.assertTrue(res)
        new_so = self._get_so_from_name(res["ref"])
        self.assertEqual("sale", res["state"])
        self._deliver_orders(new_so)
        res = self.sales_service.dispatch("get", _id=99)
        self.assertEqual("delivery", res["state"])
