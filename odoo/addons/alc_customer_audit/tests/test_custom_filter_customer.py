# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from shapely.geometry.multipolygon import MultiPolygon
from shapely.geometry.polygon import Point, Polygon

from odoo.fields import Command
from odoo.tests.common import TransactionCase


class TestCustomFilterCustomer(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        alcyon_delivery_id = cls.env.ref(
            "__setup__.deliver_carrier_alcyon", raise_if_not_found=False
        )

        if not alcyon_delivery_id:
            carrier_product = cls.env["product.product"].create(
                {
                    "name": "Test carrier product",
                    "type": "service",
                }
            )
            delivery_carrier_alcyon = cls.env["delivery.carrier"].create(
                {
                    "name": "Unittest delivery alcyon",
                    "delivery_type": "fixed",
                    "fixed_price": 10.0,
                    "product_id": carrier_product.id,
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
                "is_customer": True,
                "partner_type": "veterinary",
            }
        )

        cls.partner2 = cls.env["res.partner"].create(
            {
                "name": "Test Customer 2",
                "active": True,
                "is_customer": True,
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
                "street2": "A côté de la fontaine",
                "zip": "1010",
                "city": "Lausanne",
                "country_id": cls.env["res.country"]
                .search([("code", "=", "CH")])[0]
                .id,
                "email": "peter@ch.ch",
            }
        )
        cls.channel = cls.env["stock.release.channel"].create(
            {
                "name": "Release Channel",
            }
        )

    @staticmethod
    def _assign_multipolygon(release_channel):
        polygon = Polygon(
            [
                [4.576938, 50.441663],
                [4.605453, 50.446438],
                [4.623138, 50.435544],
                [4.606925, 50.425624],
                [4.581423, 50.430586],
            ]
        )
        multipolygon = MultiPolygon([polygon])
        release_channel.delivery_zone = multipolygon

    def test_00(self):
        """
        Data:

            one customer which is a veterinary with depot allowed
            No pharmacist on the customer
            no_pharmacist = True
        Test case:
            Set a pharmacist on the customer
        Expected result:
            no_pharmacist = False
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
            No release channel associated to the customer
            no_release_channel = True
        Test case:
            Link a release channel to the customer
        Expected result:
            no_release_channel = False
        """
        self.partner2._compute_no_release_channel()
        self.assertTrue(self.partner2.no_release_channel)
        self.partner2.stock_release_channel_ids = [Command.set([self.channel.id])]
        self.partner2._compute_no_release_channel()
        self.assertFalse(self.partner2.no_release_channel)

    def test_02(self):
        """
        Data:

            one customer which is active
            One release channel with a delivery zone
            no_release_channel = True
        Test case:
            set the geo_point of customer in delivery zone of the release channel
        Expected result:
            no_release_channel = False
        """
        self._assign_multipolygon(self.channel)
        self.partner2._compute_no_release_channel()
        self.assertTrue(self.partner2.no_release_channel)
        self.partner2.geo_point = Point([4.602541, 50.435587])
        self.partner2._compute_no_release_channel()
        self.assertFalse(self.partner2.no_release_channel)

    def test_03(self):
        """
        Data:

            one customer which is active and veterinary
            One release channel with a delivery zone
            No pharmacist on the customer
            no_release_channel = True
            no_pharmacist = True
            has_anomaly = True
        Test case:
            set the geo_point of customer in delivery zone of the release channel
            Set a pharmacist on the customer
        Expected result:
            no_release_channel = False
            no_pharmacist = False
            has_anomaly = False
        """
        self.partner2.partner_type = "veterinary"
        self._assign_multipolygon(self.channel)
        self.partner1._compute_no_pharmacist()
        self.partner2._compute_no_release_channel()
        self.partner2._compute_has_anomaly()
        self.assertTrue(self.partner2.no_pharmacist)
        self.assertTrue(self.partner2.no_release_channel)
        self.assertTrue(self.partner2.has_anomaly)
        self.partner2.pharmacist_id = self.pharmacist_1.id
        self.partner2.geo_point = Point([4.602541, 50.435587])
        self.partner2._compute_no_release_channel()
        self.partner1._compute_no_pharmacist()
        self.partner2._compute_has_anomaly()
        self.assertFalse(self.partner2.no_pharmacist)
        self.assertFalse(self.partner2.no_release_channel)
        self.assertFalse(self.partner2.has_anomaly)
