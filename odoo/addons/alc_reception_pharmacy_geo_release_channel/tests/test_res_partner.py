# Copyright 2021 ACSONE SV/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from shapely.geometry.multipolygon import MultiPolygon
from shapely.geometry.polygon import Point, Polygon

from odoo.tests.common import TransactionCase


class TestResPartner(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.env.user.company_id.delivered_by_alcyon_constraint = True
        cls.partner = cls.env["res.partner"].create(
            {"name": "Test partner", "geo_point": Point([4.602541, 50.435587])}
        )
        carrier_product = cls.env["product.product"].create(
            {
                "name": "Test carrier product",
                "type": "service",
            }
        )
        cls.delivery_alcyon = cls.env["delivery.carrier"].create(
            {
                "name": "Alcyon",
                "product_id": carrier_product.id,
                "partner_id": cls.env.user.company_id.partner_id.id,
            }
        )

        cls.default_channel = cls.env.ref(
            "stock_release_channel.stock_release_channel_default"
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

    def test_is_delivered_by_alcyon(self):
        """
        A customer is delivered by Alcyon if it's shipping_partner_id is linked to.

        any geo release channel having Alcyon as carrier partner
        """
        self.assertFalse(self.partner.is_delivered_by_alcyon)  # not delivered by Alc
        # assign delivery zone to release channel
        self._assign_multipolygon(self.default_channel)
        self.assertFalse(self.partner.is_delivered_by_alcyon)  # not delivered by Alc
        # assign Alcyon carrier to release channel
        self.partner.invalidate_recordset()
        self.default_channel.carrier_ids = self.delivery_alcyon
        self.assertTrue(self.partner.is_delivered_by_alcyon)  # delivered by Alcyon

    def test_is_delivered_by_alcyon_manual(self):
        """
        A customer is delivered by Alcyon if it's shipping_partner_id is linked to.

        any stock release channel having Alcyon as carrier partner
        """
        self.assertFalse(self.partner.is_delivered_by_alcyon)  # not delivered by Alc
        # assign Alcyon carrier to release channel
        self.partner.invalidate_recordset()
        self.default_channel.carrier_ids = self.delivery_alcyon
        self.assertFalse(
            self.partner.is_delivered_by_alcyon
        )  # not delivered by Alcyon as not in manual release channels
        self.partner.stock_release_channel_ids = self.default_channel
