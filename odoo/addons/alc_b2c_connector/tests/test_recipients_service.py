# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import random
import string

from odoo.exceptions import ValidationError

from .common import CommonCase


class TestRecipientsService(CommonCase):
    @classmethod
    def setUpClass(cls):
        super(TestRecipientsService, cls).setUpClass()

        title_id = cls.env.ref("base.res_partner_title_mister").id
        # create a b2c_partner
        cls.b2c_partner = cls.env["res.partner"].create(
            {
                "name": "EXISTING B2C PARTNER",
                "is_b2c_customer": True,
                "title": title_id,
                "street": "my first street",
                "city": "my first city",
                "zip": "1234",
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
                "sale_channel": cls.b2c_backend.sale_channel,
            }
        )

        cls.SaleOrder = cls.env["sale.order"]
        cls.payment_term_test = cls.env.ref(
            "account.account_payment_term_advance"
        ).copy()
        cls.b2c_backend.payment_term_id = cls.payment_term_test

        with cls.work_on_services() as work:
            cls.recipient_service = work.component(usage="recipients")

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
        recipient_info["country_code"] = "BE"
        recipient_info["name2"] = "My Partner Society"
        recipient_info["note"] = "Test note for delivery"

        _ = self.recipient_service.dispatch(
            "update", _id=recipient_info["id"], params=recipient_info
        )

        self.assertEqual(self.b2c_partner.street, "new_street")
        self.assertEqual(self.b2c_partner.city, "new_city")
        self.assertEqual(self.b2c_partner.zip, "4567")
        self.assertEqual(self.b2c_partner.title.name, "Madam")
        self.assertEqual(self.b2c_partner.name, "test b2cPartner")
        self.assertEqual(self.b2c_partner.suite, "My Partner Society")
        self.assertEqual(self.b2c_partner.comment, "Test note for delivery")

        self.assertEqual(self.b2c_order.partner_id.street, "new_street")
        self.assertEqual(self.b2c_order.partner_id.city, "new_city")
        self.assertEqual(self.b2c_order.partner_id.zip, "4567")
        self.assertEqual(self.b2c_order.partner_id.title.name, "Madam")
        self.assertEqual(self.b2c_order.partner_id.name, "test b2cPartner")
        self.assertEqual(self.b2c_order.partner_id.suite, "My Partner Society")
        self.assertEqual(self.b2c_order.partner_id.comment, "Test note for delivery")

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

        _ = self.recipient_service.dispatch(
            "update", _id=recipient_info["id"], params=recipient_info
        )

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

    def test_update_street_for_partner_with_started_picking(self):
        """Once the partner has a started picking, it's not possible to update the address."""
        self.b2c_order.action_confirm()
        ship = self.b2c_order.mapped("picking_ids").filtered(
            lambda p: p.picking_type_code == "outgoing"
        )
        ship.printed = True
        recipient_info = {"id": "ABC", "street": "new_street"}
        with self.assertRaises(ValidationError):
            self.recipient_service.dispatch(
                "update", _id=recipient_info["id"], params=recipient_info
            )

    def test_update_contact_fields_for_partner_with_started_picking(self):
        """We can always update the contact fields (phone, mobile, email)"""
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
            "street": self.b2c_partner.street,
            "zip": self.b2c_partner.zip,
            "city": self.b2c_partner.city,
            "note": "new note",
        }
        # when
        self.recipient_service.dispatch(
            "update", _id=recipient_info["id"], params=recipient_info
        )
        self.assertEqual(self.b2c_partner.phone, "1")
        self.assertEqual(self.b2c_partner.mobile, "2")
        self.assertEqual(self.b2c_partner.email, "3")
        self.assertEqual(self.b2c_partner.comment, "new note")
        self.assertEqual(self.b2c_partner.street, "my first street")
