# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestCustomFilterCustomer(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestCustomFilterCustomer, cls).setUpClass()
        alcyon_delivery_id = cls.env.ref(
            "__setup__.deliver_carrier_alcyon", raise_if_not_found=False
        )
        veterinary = cls.env.ref("specific_partner.partner_category_veterinary")
        delivery_template = cls.env["round.template"].create(
            {"name": "Unittest delivery template"}
        )
        cls.delivery_round_1 = cls.env["round.instance"].create(
            {"template_id": delivery_template.id, "date": "2017-01-01"}
        )

        if not alcyon_delivery_id:

            delivery_carrier_alcyon = cls.env["delivery.carrier"].create(
                {
                    "name": "Unittest delivery alcyon",
                    "delivery_type": "fixed",
                    "fixed_price": 10.0,
                    "delivery_template_id": delivery_template.id,
                }
            )
            cls.env["ir.model.data"].create(
                {
                    "module": "__setup__",
                    "name": "deliver_carrier_alcyon",
                    "model": "delivery.carrier",
                    "res_id": delivery_carrier_alcyon.id,
                }
            )

        cls.partner1 = cls.env["res.partner"].create(
            {
                "name": "Test Customer 1",
                "active": True,
                "customer": True,
                "alcyon_category_id": veterinary.id,
            }
        )

        cls.partner2 = cls.env["res.partner"].create(
            {
                "name": "Test Customer 2",
                "active": True,
                "customer": True,
                "property_delivery_carrier_id": cls.env.ref(
                    "__setup__.deliver_carrier_alcyon", raise_if_not_found=False
                ).id,
            }
        )

        cls.pharmacist_1 = cls.env["res.partner"].create(
            {
                "ref": "116",
                "name": "Peter",
                "street": "Chemin des Oies, 1",
                "street2": u"A côté de la fontaine",
                "zip": "1010",
                "city": "Lausanne",
                "country_id": cls.env["res.country"]
                .search([("code", "=", "CH")])[0]
                .id,
                "phone": "021123123",
                "fax": "021121212",
                "email": "peter@ch.ch",
            }
        )

    def test_00(self):
        """
        Data:
            one customer which is a veterinary with depot allowed
        Test case:
            No pharmacist on the customer : this should put the flag "no_pharmacist" to True
        Expected result:
            no_pharmacist = True
        """

        self.partner1._compute_no_pharmacist()
        self.assertTrue(self.partner1.no_pharmacist)

        self.partner1.pharmacist_id = self.pharmacist_1.id
        self.partner1._compute_no_pharmacist()
        self.assertFalse(self.partner1.no_pharmacist)

    def test_01(self):
        """
        Data:
            one customer which is active
        Test case:
            No delivery round associated to the customer : no_delivery_round should be true
        Expected result:
            no_delivery_round = True
        """

        self.partner2._compute_no_delivery_round()
        self.assertTrue(self.partner2.no_delivery_round)

        itinerary = self.env["round.itinerary"].create(
            {
                "name": "Itinerary 17C",
                "code": "T17C",
                "sequence": 22,
                "partner_position_ids": [
                    (0, 0, {"sequence": 10, "partner_id": self.partner2.id})
                ],
            }
        )
        self.delivery_round_1.itinerary_ids = itinerary
        self.partner2._compute_no_delivery_round()
        self.assertFalse(self.partner2.no_delivery_round)
