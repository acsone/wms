# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import random

from odoo.tests.common import TransactionCase


class TestForceRelocalization(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        vals_partner = {
            "name": "Unittest partner",
            "city": "Ramillies",
            "zip": "1367",
            "email": "rd@odoo.con",
            "street": "9, rue des bourlottes",
            "country_id": cls.env.ref("base.be").id,
            "ref": "12344566777878",
            "customer_rank": 1,
            "is_b2c_customer": False,
            "partner_latitude": 50.62998,
            "partner_longitude": 4.86337,
        }
        cls.partner1 = cls.env["res.partner"].create(vals_partner)

    def _geolocalize(self):
        partner_latitude = 50.62998 + random.randint(0, 1000) / 1000
        partner_longitude = 4.86337 + random.randint(0, 1000) / 1000
        self.partner1.write(
            {
                "partner_latitude": partner_latitude,
                "partner_longitude": partner_longitude,
            }
        )

    def test_change_address(self):
        self.assertFalse(self.partner1.coordinates_should_be_checked)
        self.partner1.write({"street": "rue du malcampé"})
        self.assertTrue(self.partner1.coordinates_should_be_checked)

        self._geolocalize()
        self.assertFalse(self.partner1.coordinates_should_be_checked)

    def test_change_address_twice(self):
        self.partner1.write({"street": "rue du malcampé"})
        self.assertTrue(self.partner1.coordinates_should_be_checked)

        self.partner1.write({"street": "rue de laloux"})
        self.assertTrue(self.partner1.coordinates_should_be_checked)

        self._geolocalize()
        self.assertFalse(self.partner1.coordinates_should_be_checked)

    def test_just_geolocalize(self):
        self._geolocalize()
        self.assertFalse(self.partner1.coordinates_should_be_checked)
