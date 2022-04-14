# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from contextlib import contextmanager

from odoo.addons.shopinvader.tests.common import CommonCase


class TestEshopCustomerSalesPerson(CommonCase):
    @classmethod
    def setUpClass(cls):
        super(TestEshopCustomerSalesPerson, cls).setUpClass()
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

    @contextmanager
    def customer_service(self, partner=None):
        with self.work_on_services(
            partner=partner, shopinvader_session=self.shopinvader_session
        ) as work:
            yield work.component(usage="customer")

    def _assert_sales_person(self, partner_customer, partner_sales_person):
        with self.customer_service(partner_customer) as service:
            self.maxDiff = 2000
            res = service.dispatch("get_sales_person")
            self.assertDictEqual(
                {
                    "name": partner_sales_person.name,
                    "address": self.env["res.partner.serializer"]._to_json_address(
                        partner_sales_person
                    ),
                },
                res,
            )

    def test_partner_without_sales_person(self):
        # the sales person must be the backend company
        self._assert_sales_person(
            self.partner_without_sales_person, self.backend.company_id.partner_id
        )

    def test_partner_with_sales_person(self):
        # the sales person must be the partner of the linked sales person user_id
        self._assert_sales_person(
            self.partner_with_sales_person, self.sales_person_user.partner_id
        )
