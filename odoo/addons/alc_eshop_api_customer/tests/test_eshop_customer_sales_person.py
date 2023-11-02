# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import json

from odoo.addons.extendable_fastapi.tests.common import FastAPITransactionCase
from odoo.addons.shopinvader_schema_address.schemas import Address

from ..routers import customer_router


class TestEshopCustomerSalesPerson(FastAPITransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.default_fastapi_router = customer_router
        cls.data = {
            "email": "new@customer.example.com",
            "name": "Purple",
            "street": "Rue du jardin",
            "zip": "43110",
            "city": "Aurec sur Loire",
            "phone": "0485485454",
            "mobile": "0685485454",
            "country": {"id": cls.env.ref("base.fr").id},
            "is_company": False,
        }
        cls.partner_without_sales_person = cls.env["res.partner"].create(
            {"name": "without sales person"}
        )
        cls.sales_person_user = cls.env["res.users"].create(
            {"name": "sales_person", "login": "login"}
        )
        cls.partner_with_sales_person = cls.env["res.partner"].create(
            {"name": "with sales person", "user_id": cls.sales_person_user.id}
        )

    def _assert_sales_person(self, partner_customer, partner_sales_person):
        with self._create_test_client(partner=partner_customer) as test_client:
            self.maxDiff = 2000
            response = test_client.get("/customer/sales_person")
            self.assertEqual(response.status_code, 200)
            res = response.json()
            self.assertDictEqual(
                {
                    "name": partner_sales_person.name,
                    "address": json.loads(
                        Address.from_res_partner(partner_sales_person).model_dump_json()
                    ),
                },
                res,
            )

    def test_partner_without_sales_person(self):
        # the sales person must be the backend company
        self._assert_sales_person(
            self.partner_without_sales_person, self.env.company.partner_id
        )

    def test_partner_with_sales_person(self):
        # the sales person must be the partner of the linked sales person user_id
        self._assert_sales_person(
            self.partner_with_sales_person, self.sales_person_user.partner_id
        )

    def test_customer_info(self):
        partner = self.partner_without_sales_person
        with self._create_test_client(partner=partner) as test_client:
            self.maxDiff = 2000
            response = test_client.get("/customer")
            self.assertEqual(response.status_code, 200)
            res = response.json()
            self.assertDictEqual(
                {
                    "data": json.loads(
                        Address.from_res_partner(partner).model_dump_json()
                    ),
                },
                res,
            )
