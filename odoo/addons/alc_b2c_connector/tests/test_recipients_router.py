# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import random
import string

from fastapi import status
from requests import Response

from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tools.misc import mute_logger

from ..routers.recipients import router as recipients_router
from ..schemas.country_code import CountryCode
from .common import CommonB2CServiceCase


class TestRecipientsService(CommonB2CServiceCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.default_fastapi_router = recipients_router

        title_id = cls.env.ref("base.res_partner_title_mister").id
        cls.belgium = cls.env.ref("base.be")
        # create a b2c_partner
        cls.b2c_partner = cls.env["res.partner"].create(
            {
                "name": "EXISTING B2C PARTNER",
                "is_b2c_customer": True,
                "title": title_id,
                "street": "my first street",
                "city": "my first city",
                "zip": "1234",
                "partner_type": "student_like",
                "ref": f"{cls.sale_channel.name}_ABC",
                "alc_b2c_client_id": cls.b2c_client.id,
                "email": "b2c@b2c.be",
                "country_id": cls.belgium.id,
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
                "partner_type": "veterinary",
                "ref": "Amazon_",
                "email": "vt@vt.be",
                "customer_payment_mode_id": cls.vt_payment_mode.id,
            }
        )
        cls.SaleOrder = cls.env["sale.order"]
        cls.payment_term_test = cls.env.ref(
            "account.account_payment_term_advance"
        ).copy()
        cls.b2c_client.payment_term_id = cls.payment_term_test

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

    def setUp(self):
        super().setUp()
        # create a b2c sale_order
        self.b2c_order = self.env["sale.order"].create(
            {
                "b2c_ref": 10,
                "partner_id": self.b2c_partner.id,
                "partner_invoice_id": self.vt_partner.id,
                "partner_shipping_id": self.vt_partner.id,
                "pricelist_id": self.pricelist_id.id,
                "order_line": [
                    Command.create(
                        {
                            "b2c_ref": 1,
                            "product_id": self.saleable_product.id,
                            "name": self.saleable_product.name,
                            "product_uom": self.saleable_product.uom_id.id,
                            "product_uom_qty": 10,
                        },
                    )
                ],
                "sale_channel_id": self.sale_channel.id,
            }
        )

    def test_get_b2c_recipient_info(self):
        """
        Data:

            1 existing b2c partner
        Test case:
            Get recipient info with the b2c ref
        Expected result:
            The recipient info
        """
        with self._create_test_client() as client:
            response: Response = client.get(
                "/recipients/ABC", headers={"api-key": "1234"}
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        res = response.json()
        self.assertTrue(res)
        self.assertEqual(res["id"], "ABC")
        self.assertEqual(res["name"], "EXISTING B2C PARTNER")
        self.assertEqual(res["street"], "my first street")
        self.assertEqual(res["city"], "my first city")
        self.assertEqual(res["zip"], "1234")

    def test_update_existing(self):
        """
        Data:

            An existing b2c customer
        Test case:
            Updating the address, name and title
        Expected result:
            Address, name and title are updated both on the partner and the SO
        """
        recipient_info = {}
        recipient_info["id"] = "ABC"
        recipient_info["street"] = "new_street"
        recipient_info["title"] = "mm"
        recipient_info["first_name"] = "test"
        recipient_info["last_name"] = "b2cPartner"
        recipient_info["zip"] = "4567"
        recipient_info["city"] = "new_city"
        recipient_info["country_code"] = CountryCode.BE
        recipient_info["name2"] = "My Partner Society"
        recipient_info["note"] = "Test note for delivery"
        with self._create_test_client() as client:
            response: Response = client.post(
                "/recipients/ABC/update",
                headers={"api-key": "1234"},
                json=recipient_info,
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())

        self.assertEqual(self.b2c_partner.street, "new_street")
        self.assertEqual(self.b2c_partner.city, "new_city")
        self.assertEqual(self.b2c_partner.zip, "4567")
        self.assertEqual(self.b2c_partner.title.name, "Madam")
        self.assertEqual(self.b2c_partner.name, "test b2cPartner")
        self.assertEqual(self.b2c_partner.suite, "My Partner Society")
        self.assertEqual(str(self.b2c_partner.comment), "<p>Test note for delivery</p>")

        self.assertEqual(self.b2c_order.partner_id.street, "new_street")
        self.assertEqual(self.b2c_order.partner_id.city, "new_city")
        self.assertEqual(self.b2c_order.partner_id.zip, "4567")
        self.assertEqual(self.b2c_order.partner_id.title.name, "Madam")
        self.assertEqual(self.b2c_order.partner_id.name, "test b2cPartner")
        self.assertEqual(self.b2c_order.partner_id.suite, "My Partner Society")
        self.assertEqual(
            str(self.b2c_order.partner_id.comment), "<p>Test note for delivery</p>"
        )

    def test_update_existing_street_only(self):
        """
        Data:

            An existing b2c customer
        Test case:
            Updating the street only
        Expected result:
           Street is updated, the rest stays the same
        """
        recipient_info = {}
        recipient_info["id"] = "ABC"
        recipient_info["street"] = "new_street"
        with self._create_test_client() as client:
            response: Response = client.post(
                "/recipients/ABC/update",
                headers={"api-key": "1234"},
                json=recipient_info,
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())

        self.assertEqual(self.b2c_partner.street, "new_street")
        self.assertEqual(self.b2c_partner.city, "my first city")
        self.assertEqual(self.b2c_partner.zip, "1234")
        self.assertEqual(self.b2c_partner.title.name, "Mister")
        self.assertEqual(self.b2c_partner.name, "EXISTING B2C PARTNER")

        self.assertEqual(self.b2c_order.partner_id.street, "new_street")
        self.assertEqual(self.b2c_order.partner_id.city, "my first city")
        self.assertEqual(self.b2c_order.partner_id.zip, "1234")
        self.assertEqual(self.b2c_order.partner_id.title.name, "Mister")
        self.assertEqual(self.b2c_order.partner_id.name, "EXISTING B2C PARTNER")

    @mute_logger(
        "odoo.addons.alc_b2c_connector.models.res_partner",
        "odoo.addons.alc_b2c_connector.models.res_country",
    )
    def test_update_street_for_partner_with_started_picking(self):
        """Once the partner has a started picking, it's not possible to update the address."""

        self.b2c_order.partner_id = self.b2c_partner
        self.b2c_order.action_confirm()
        ship = self.b2c_order.mapped("picking_ids").filtered(
            lambda p: p.picking_type_code == "outgoing"
        )
        ship.printed = True
        fields = {"city", "country_code", "street", "street2", "first_name", "zip"}

        for field in fields:

            with self.assertRaises(
                ValidationError,
                msg="You cannot update this address since there are already closed "
                "Sale Orders for this partner.",
            ):
                self.env["res.partner"]._update_b2c_recipient(
                    "ABC",
                    self.b2c_client,
                    {
                        "id": "ABC",
                        field: CountryCode.BF if field == "country_code" else "X",
                    },
                )

    def test_update_contact_fields_for_partner_with_started_picking(self):
        """We can always update the contact fields (phone, mobile, email)."""
        self.b2c_order.action_confirm()
        ship = self.b2c_order.mapped("picking_ids").filtered(
            lambda p: p.picking_type_code == "outgoing"
        )
        ship.printed = True
        recipient_info = {
            "id": "ABC",
            "phone": "1",
            "mobile": "2",
            "email": "3",
            "title": "mr",  # the value that is already set
            "country_code": "BE",  # the value that is already set
            "street": self.b2c_partner.street,
            "zip": self.b2c_partner.zip,
            "city": self.b2c_partner.city,
            "note": "new note",
        }
        with self._create_test_client() as client:
            response: Response = client.post(
                "/recipients/ABC/update",
                headers={"api-key": "1234"},
                json=recipient_info,
            )

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        self.assertEqual(self.b2c_partner.phone, "1")
        self.assertEqual(self.b2c_partner.mobile, "2")
        self.assertEqual(self.b2c_partner.email, "3")
        self.assertEqual(str(self.b2c_partner.comment), "<p>new note</p>")
        self.assertEqual(self.b2c_partner.street, "my first street")

    def test_update_nullable_fields(self):
        """Updatable fields can be erased by passing None."""
        self.b2c_partner.write({"phone": "0", "mobile": "1", "comment": "C"})
        recipient_info = {"id": "ABC", "phone": None, "mobile": None, "note": None}
        with self._create_test_client() as client:
            response: Response = client.post(
                "/recipients/ABC/update",
                headers={"api-key": "1234"},
                json=recipient_info,
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        self.assertFalse(self.b2c_partner.phone)
        self.assertFalse(self.b2c_partner.mobile)
        self.assertFalse(self.b2c_partner.comment)

    @mute_logger("odoo.addons.alc_b2c_connector.models.res_partner")
    def test_name2(self):
        """Suite can be nulled, and is not updatable after a picking is started."""
        self.b2c_order.partner_id = self.b2c_partner
        self.b2c_partner.suite = "C"
        with self._create_test_client() as client:
            response: Response = client.post(
                "/recipients/ABC/update",
                headers={"api-key": "1234"},
                json={"id": "ABC", "name2": None},
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        self.assertFalse(self.b2c_partner.suite)

        self.b2c_order.action_confirm()
        self.b2c_order.mapped("picking_ids").write({"printed": True})
        with self.assertRaises(ValidationError):
            self.env["res.partner"]._update_b2c_recipient(
                "ABC",
                self.b2c_client,
                {"id": "ABC", "name2": "S"},
            )

    def test_update_recipient_if_allowed_on_b2c_backend(self):
        self.b2c_client.allow_customer_modifications = True
        self.b2c_order.action_confirm()
        ship = self.b2c_order.mapped("picking_ids").filtered(
            lambda p: p.picking_type_code == "outgoing"
        )
        ship.printed = True
        recipient_info = {
            "id": "ABC",
            "first_name": "RENAMED",
            "last_name": "B2C PARTNER",
            "street": "new street info no check",
            "zip": "new zip info no check",
            "city": "new city info no check",
        }
        with self._create_test_client() as client:
            response: Response = client.post(
                "/recipients/ABC/update",
                headers={"api-key": "1234"},
                json=recipient_info,
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        self.assertEqual(self.b2c_partner.street, "new street info no check")
        self.assertEqual(self.b2c_partner.zip, "new zip info no check")
        self.assertEqual(self.b2c_partner.city, "new city info no check")
        self.assertEqual(self.b2c_partner.name, "RENAMED B2C PARTNER")
