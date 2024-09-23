# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from fastapi import status
from freezegun import freeze_time
from pydantic._internal._generate_schema import GenerateSchema
from pydantic_core import core_schema
from requests import Response

from odoo import fields
from odoo.exceptions import MissingError, ValidationError
from odoo.tools.misc import mute_logger

from ..routers.sales import router as sales_router
from .common import CommonB2CSaleServiceCase

ISO_DT_WITH_TZ = "2020-05-28T13:45:47+02:00"

# HACK to ensure pydantic generates the correct schema for datetime
# when used with freezegun


initial_match_type = GenerateSchema.match_type


def match_type(self, obj):
    if getattr(obj, "__name__", None) == "datetime":
        return core_schema.datetime_schema()
    return initial_match_type(self, obj)


GenerateSchema.match_type = match_type

# END OF HACK


class TestSalesService(CommonB2CSaleServiceCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.default_fastapi_router = sales_router

    def test_00(self):
        """
        Data:

            1 existing SO
        Test case:
            Get order info with the b2c ref
        Expected result:
            The so info
        """
        with self._create_test_client() as client:
            response: Response = client.get("/sales/10", headers={"api-key": "1234"})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        res = response.json()
        self.assertTrue(res)
        self.assertEqual(res["state"], self.b2c_order.state)
        self.assertEqual(res["ref"], self.b2c_order.name)
        self.assertEqual(res["id"], 10)
        self.assertFalse(res["confirmation_date"])

    @mute_logger("odoo.addons.alc_b2c_connector.models.sale_order")
    def test_01(self):
        """
        Test case:

            Get order info with an unknown b2c ref
        Expected result:
            Missing error is raised
        """
        with self.assertRaises(MissingError):
            self.env["sale.order"]._get_order_from_b2c_ref(9999, self.b2c_client)

    def test_02(self):
        """
        Data:

            1 existing SO
        Test case:
            Search order info with the b2c ref
        Expected result:
            The so info
        """
        with self._create_test_client() as client:
            response: Response = client.get(
                "/sales/search",
                headers={"api-key": "1234"},
                params={"ids[]": [10]},
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        res = response.json()
        self.assertEqual(res["size"], 1)
        result = res["data"][0]
        self.assertEqual(result["state"], self.b2c_order.state)
        self.assertEqual(result["ref"], self.b2c_order.name)
        self.assertEqual(result["id"], 10)
        self.assertFalse(result["confirmation_date"])

    @freeze_time("2020-05-28 11:45:47")
    def test_04(self):
        """
        Access Denied by ACLs for operation     Data:

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
        with self._create_test_client() as client:
            response: Response = client.post(
                "/sales/create",
                headers={"api-key": "1234"},
                json=params,
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        res = response.json()

        self.assertTrue(res)
        new_so = self._get_so_from_name(res["ref"])
        self.assertTrue(new_so)
        self.assertEqual(
            new_so.partner_id.ref,
            f"{self.b2c_client.sale_channel_id.code}_{recipient_info['id']}".format(),
        )
        self.assertEqual(new_so.partner_invoice_id, self.vt_partner)
        self.assertEqual(new_so.partner_shipping_id, self.vt_partner)
        self.assertEqual(new_so.partner_id.sale_reason_backorder_strategy, "cancel")
        self.assertEqual(
            new_so.date_order, fields.Datetime.to_datetime("2020-05-28 11:45:47")
        )
        self.assertTrue(self.b2c_client.pricelist_id)
        self.assertEqual(new_so.pricelist_id, self.b2c_client.pricelist_id)
        self.assertTrue(self.b2c_client.sale_team_id)
        self.assertEqual(new_so.team_id, self.b2c_client.sale_team_id)
        self.assertTrue(self.b2c_client.payment_mode_id)
        self.assertEqual(new_so.payment_mode_id, self.b2c_client.payment_mode_id)
        self.assertEqual(self.b2c_client.payment_term_id, self.payment_term_test)
        self.assertEqual(new_so.payment_term_id, self.payment_term_test)
        self.assertTrue(new_so.supplier_promotion_allowed)
        self.assertEqual(1, len(new_so.order_line))
        sol = new_so.order_line
        self.assertEqual(sol.product_id, self.saleable_product)
        self.assertEqual(sol.discount3, 0)  # discount in %
        self.assertEqual(sol.price_unit, 10)
        self.assertEqual(sol.product_qty, 10)

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
        self.b2c_client.payment_mode_id = False
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
        with self._create_test_client() as client:
            response: Response = client.post(
                "/sales/create",
                headers={"api-key": "1234"},
                json=params,
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        res = response.json()
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
            self.b2c_client.picking_policy = policy
            recipient_info = self._gen_recipent()
            params = {
                "id": i + 100,
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
            with self._create_test_client() as client:
                response: Response = client.post(
                    "/sales/create",
                    headers={"api-key": "1234"},
                    json=params,
                )
            self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
            res = response.json()
            self.assertTrue(res)
            new_so = self._get_so_from_name(res["ref"])
            self.assertTrue(new_so)
            self.assertEqual(new_so.picking_policy, policy)

    @mute_logger("odoo.addons.alc_b2c_connector.models.res_partner")
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
            self.env["sale.order"]._create_from_b2c(params, self.b2c_client)

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
        with self._create_test_client() as client:
            response: Response = client.post(
                "/sales/create",
                headers={"api-key": "1234"},
                json=params,
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        res = response.json()
        self.assertTrue(res)
        new_so = self._get_so_from_name(res["ref"])
        self.assertTrue(new_so)
        self.assertEqual(new_so.partner_id, self.b2c_partner)
        self.assertEqual(new_so.partner_invoice_id, self.vt_partner)
        self.assertEqual(new_so.partner_shipping_id, self.vt_partner)

    @mute_logger("odoo.addons.alc_b2c_connector.models.sale_order")
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
            self.env["sale.order"]._create_from_b2c(params, self.b2c_client)

    @mute_logger("odoo.addons.alc_b2c_connector.models.sale_order")
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
            self.env["sale.order"]._create_from_b2c(params, self.b2c_client)

    @freeze_time("2020-05-28 11:45:47")
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
        with self._create_test_client() as client:
            response: Response = client.post(
                "/sales/create",
                headers={"api-key": "1234"},
                json=params,
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        res = response.json()
        self.assertTrue(res)
        new_so = self._get_so_from_name(res["ref"])
        self.assertEqual(2, len(new_so.order_line))
        self.assertEqual("sale", new_so.state)
        self.assertDictEqual(
            {
                "lines": [
                    {
                        "sku": "12345",
                        "line_id": 2,
                        "qty_ordered": 10,
                        "qty_returned": 0,
                        "qty_delivered": 0,
                        "qty_cancelled": 0,
                        "qty_backorder": 5,
                    },
                    {
                        "sku": "23456",
                        "line_id": 3,
                        "qty_ordered": 1,
                        "qty_returned": 0,
                        "qty_delivered": 0,
                        "qty_cancelled": 0,
                        "qty_backorder": 0,
                    },
                ]
            },
            {"lines": res.get("lines")},
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
        with self._create_test_client() as client:
            response: Response = client.post(
                "/sales/create",
                headers={"api-key": "1234"},
                json=params,
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        res = response.json()
        self.assertTrue(res)
        new_so = self._get_so_from_name(res["ref"])
        self.assertEqual("sale", res["state"])
        self._deliver_orders(new_so)
        with self._create_test_client() as client:
            response: Response = client.get(
                "/sales/99",
                headers={"api-key": "1234"},
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        res = response.json()
        self.assertEqual("delivery", res["state"])

    def test_10_01(self):
        """
        Test case:

            1. Create a new SO with 2 lines.
               5 saleable products are in stock
               110  saleable product2s are in stock

            2. Deliver available product and add tracking information
        Expected result:
            1 state is 'sale'
            2 state is 'delivery' and deliveries info are available
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
        with self._create_test_client() as client:
            response: Response = client.post(
                "/sales/create",
                headers={"api-key": "1234"},
                json=params,
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        res = response.json()
        self.assertTrue(res)
        new_so = self._get_so_from_name(res["ref"])
        self.assertEqual("sale", res["state"])
        self._deliver_orders(new_so)
        new_so.picking_ids.write({"carrier_tracking_ref": "AZ123"})
        with self._create_test_client() as client:
            response: Response = client.get(
                "/sales/99",
                headers={"api-key": "1234"},
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        res = response.json()
        self.assertEqual("delivery", res["state"])
        self.assertIn("deliveries", res)
        delivery = res["deliveries"][0]
        self.assertEqual(delivery["tracking_reference"], "AZ123")
        self.assertEqual(
            delivery["delivery_date"], fields.Date.to_string(fields.Date.today())
        )
        self.assertFalse(delivery["carrier"])
        self.assertFalse(new_so.carrier_id)

    def test_11(self):
        """
        Data:

            An existing veterinary
        Test case:
            Create a new SO for a new partner and the existing veterinary
            Partner with a specific country...
        Expected result:
            A new partner is created with the diven country
        """
        recipient_info = self._gen_recipent()
        recipient_info["country_code"] = "BE"
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
        with self._create_test_client() as client:
            response: Response = client.post(
                "/sales/create",
                headers={"api-key": "1234"},
                json=params,
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        res = response.json()
        self.assertTrue(res)
        new_so = self._get_so_from_name(res["ref"])
        self.assertEqual(
            new_so.partner_id.ref,
            f"{self.b2c_client.sale_channel_id.code}_{recipient_info['id']}",
        )
        self.assertEqual("BE", new_so.partner_id.country_id.code)

        # we now validate the order
        new_so._action_confirm()
        self.assertEqual(new_so.state, "sale")

        # from here it's no more possible to update the partner. We call the
        # service with the same info and it should work
        self._deliver_orders(new_so)

        # a new so can be safely created
        params = {
            "id": 3,
            "customer_ref": self.vt_partner.ref,
            "date": ISO_DT_WITH_TZ,
            "recipient": recipient_info,
            "lines": [
                {
                    "line_id": 3,
                    "sku": self.saleable_product.default_code,
                    "quantity": 10,
                }
            ],
        }
        with self._create_test_client() as client:
            response: Response = client.post(
                "/sales/create",
                headers={"api-key": "1234"},
                json=params,
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())

    def test_12(self):
        """
        Data:

            1 existing SO
        Test case:
            Cancel the so while no picking is started for it
        Expected result:
            The so is cancelled
        """
        with self._create_test_client() as client:
            response: Response = client.post(
                f"/sales/{self.b2c_order.b2c_ref}/cancel",
                headers={"api-key": "1234"},
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        self.assertEqual("cancel", self.b2c_order.state)

    def test_13(self):
        """
        Data:

            1 existing SO
        Test case:
            Try to cancel the SO while the picking is printed
        Expected result:
            The so is not cancelled
        """
        self._deliver_orders(self.b2c_order)
        self.b2c_order.picking_ids.do_print_picking()
        with self._create_test_client() as client:
            response: Response = client.post(
                f"/sales/{self.b2c_order.b2c_ref}/cancel",
                headers={"api-key": "1234"},
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        self.assertIn(self.b2c_order.state, ["sale", "done"])

    def test_14(self):
        """
        Data:

            An existing SO
        Test case:
            Update one line of the SO  (change the quantity of product) before it is started
        Expected result:
            one line update, second one stays unchanged
        """
        order_line2 = self.env["sale.order.line"].create(
            {
                "order_id": self.b2c_order.id,
                "b2c_ref": 2,
                "product_id": self.saleable_product_2.id,
                "name": self.saleable_product_2.name,
                "product_uom": self.saleable_product_2.uom_id.id,
                "product_uom_qty": 10,
            }
        )

        order_line1 = self.b2c_order.order_line[0]

        self.assertEqual(order_line1.product_uom_qty, 10)
        self.assertEqual(order_line2.product_uom_qty, 10)

        params = {
            "id": 10,
            "lines": [
                {
                    "line_id": 1,
                    "sku": self.saleable_product.default_code,
                    "quantity": 10,
                },
                {
                    "line_id": 2,
                    "sku": self.saleable_product_2.default_code,
                    "quantity": 5,
                },
            ],
        }
        self.b2c_order.action_confirm()
        self.assertIn(self.b2c_order.state, ["sale", "done"])

        with self._create_test_client() as client:
            response: Response = client.post(
                f"/sales/{self.b2c_order.b2c_ref}/update",
                headers={"api-key": "1234"},
                json=params,
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        self.assertEqual(self.b2c_order.order_line[0].product_uom_qty, 10)
        self.assertEqual(self.b2c_order.order_line[1].product_uom_qty, 5)
        self.assertEqual(self.b2c_order.state, "sale")

    def test_15(self):
        """
        Data:

            An existing SO
        Test case:
            Add a new line to the sale order
        Expected result:
            sale order now has 2 lines
        """
        order_line1 = self.b2c_order.order_line[0]
        self.assertEqual(order_line1.product_uom_qty, 10)
        self.assertEqual(len(self.b2c_order.order_line), 1)

        params = {
            "id": 10,
            "lines": [
                {
                    "line_id": 1,
                    "sku": self.saleable_product.default_code,
                    "quantity": 10,
                },
                {
                    "line_id": 2,
                    "sku": self.saleable_product_2.default_code,
                    "quantity": 35,
                },
            ],
        }

        self.b2c_order.action_confirm()
        self.assertIn(self.b2c_order.state, ["sale", "done"])
        with self._create_test_client() as client:
            response: Response = client.post(
                f"/sales/{self.b2c_order.b2c_ref}/update",
                headers={"api-key": "1234"},
                json=params,
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())

        self.assertEqual(self.b2c_order.order_line[0].product_uom_qty, 10)
        self.assertEqual(self.b2c_order.order_line[1].product_uom_qty, 35)
        self.assertEqual(len(self.b2c_order.order_line), 2)
        self.assertIn(self.b2c_order.state, ["sale", "done"])

    @mute_logger("odoo.addons.alc_b2c_connector.models.sale_order")
    def test_16(self):
        """
        Data:

            An existing SO
        Test case:
            Try to update a sale order that is already out for delivery
        Expected result:
            raise error
        """
        order_line1 = self.b2c_order.order_line[0]
        self.assertEqual(order_line1.product_uom_qty, 10)
        self.assertEqual(len(self.b2c_order.order_line), 1)

        params = {
            "id": 10,
            "lines": [
                {
                    "line_id": 1,
                    "sku": self.saleable_product.default_code,
                    "quantity": 10,
                },
                {
                    "line_id": 2,
                    "sku": self.saleable_product_2.default_code,
                    "quantity": 35,
                },
            ],
        }

        self._deliver_orders(self.b2c_order)
        with self._create_test_client() as client:
            response: Response = client.get(
                "/sales/10",
                headers={"api-key": "1234"},
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        res = response.json()
        self.assertEqual("delivery", res["state"])
        with self.assertRaises(ValidationError):
            self.b2c_order._update_from_b2c(params, self.b2c_client)

    def test_update_existing_recipient(self):
        recipient_info = {
            "id": "ABC",
            "title": "mr",
            "last_name": "B2C PARTNER",
            "first_name": "EXISTING",
            "street": "test street",
            "zip": "1234",
            "city": "test city",
            "email": "b2c@b2c.be",
            "name2": "My company",
            "note": "Specific note for delivery",
        }
        params = {"id": 10, "recipient": recipient_info}
        self.assertFalse(self.b2c_order.partner_id.zip)
        self.b2c_order.action_confirm()

        with self._create_test_client() as client:
            response: Response = client.post(
                f"/sales/{self.b2c_order.b2c_ref}/update",
                headers={"api-key": "1234"},
                json=params,
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())

        self.assertEqual(self.b2c_order.partner_id.zip, "1234")
        self.assertEqual(self.b2c_order.partner_id.suite, "My company")
        self.assertEqual(
            str(self.b2c_order.partner_id.comment), "<p>Specific note for delivery</p>"
        )

    def test_update_new_recipient(self):
        recipient_info = self._gen_recipent()
        params = {"id": 10, "recipient": recipient_info}
        old_partner = self.b2c_order.partner_id

        with self._create_test_client() as client:
            response: Response = client.post(
                f"/sales/{self.b2c_order.b2c_ref}/update",
                headers={"api-key": "1234"},
                json=params,
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())

        self.assertNotEqual(self.b2c_order.partner_id, old_partner)
        self.assertEqual(self.b2c_order.partner_id.zip, recipient_info["zip"])

    def test_update_existing_remove_field(self):
        self.b2c_order.partner_id.phone = "0032"
        recipient_info = {
            "id": "ABC",
            "last_name": "B2C PARTNER",
            "first_name": "EXISTING",
            "phone": None,
            "email": "b2c@b2c.be",
        }
        params = {"id": 10, "recipient": recipient_info}
        with self._create_test_client() as client:
            response: Response = client.post(
                f"/sales/{self.b2c_order.b2c_ref}/update",
                headers={"api-key": "1234"},
                json=params,
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())

        self.assertFalse(self.b2c_order.partner_id.phone)

    @mute_logger("odoo.addons.alc_b2c_connector.models.sale_order")
    def test_update_existing_missing_payload_raises(self):
        params = {"id": 10}
        with self.assertRaises(ValidationError):
            self.b2c_order._update_from_b2c(params, self.b2c_client)

    def test_create_two_so_for_same_partner(self):
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
        with self._create_test_client() as client:
            response: Response = client.post(
                "/sales/create",
                headers={"api-key": "1234"},
                json=params,
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        res = response.json()
        self.assertTrue(res)
        new_so = self._get_so_from_name(res["ref"])
        self._deliver_orders(new_so)
        params2 = {
            "id": 3,
            "customer_ref": self.vt_partner.ref,
            "date": ISO_DT_WITH_TZ,
            "recipient": recipient_info,
            "lines": [
                {
                    "line_id": 3,
                    "sku": self.saleable_product.default_code,
                    "quantity": 10,
                }
            ],
        }
        with self._create_test_client() as client:
            response: Response = client.post(
                "/sales/create",
                headers={"api-key": "1234"},
                json=params2,
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        res2 = response.json()
        self.assertTrue(res2)
