# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from shapely.geometry.multipolygon import MultiPolygon
from shapely.geometry.polygon import Point, Polygon

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestResPartnerSearch(TransactionCase):
    def setUp(self):
        super().setUp()
        self.env = self.env(context=dict(self.env.context, tracking_disable=True))
        self.ResPartner = self.env["res.partner"]
        self.StockReleaseChannel = self.env["stock.release.channel"]

        self.polygon1 = Polygon([(0, 0), (0, 10), (10, 10), (10, 0), (0, 0)])
        self.polygon2 = Polygon([(5, 5), (5, 15), (15, 15), (15, 5), (5, 5)])
        self.polygon3 = Polygon([(20, 20), (20, 30), (30, 30), (30, 20), (20, 20)])

        self.point1 = Point(2, 2)
        self.point2 = Point(7, 7)
        self.point3 = Point(25, 25)

        self.channel_alpha = self.StockReleaseChannel.create(
            {
                "name": "Alpha Channel",
                "delivery_zone": MultiPolygon([self.polygon1]),
            }
        )
        self.channel_beta = self.StockReleaseChannel.create(
            {
                "name": "Beta Channel",
                "delivery_zone": MultiPolygon([self.polygon2]),
            }
        )
        self.channel_gamma = self.StockReleaseChannel.create(
            {
                "name": "Gamma Channel",
                "delivery_zone": MultiPolygon([self.polygon3]),
            }
        )

        self.partner_a = self.ResPartner.create(
            {
                "name": "Partner A",
                "geo_point": self.point1,
                "in_geo_release_channel": True,
            }
        )

        self.partner_b = self.ResPartner.create(
            {
                "name": "Partner B",
                "geo_point": self.point2,
                "in_geo_release_channel": True,
            }
        )

        self.partner_c = self.ResPartner.create(
            {
                "name": "Partner C",
                "geo_point": self.point3,
                "in_geo_release_channel": True,
            }
        )
        self.partner_d = self.ResPartner.create(
            {
                "name": "Partner D",
                "geo_point": False,
                "in_geo_release_channel": True,
            }
        )

    def test_setup(self):
        self.assertEqual(
            self.partner_a.located_in_stock_release_channel_ids, self.channel_alpha
        )
        self.assertEqual(
            self.partner_b.located_in_stock_release_channel_ids,
            self.channel_alpha | self.channel_beta,
        )
        self.assertEqual(
            self.partner_c.located_in_stock_release_channel_ids, self.channel_gamma
        )
        self.assertFalse(self.partner_d.located_in_stock_release_channel_ids)

    def test_search_located_in_stock_release_channel_ids_like(self):
        partners = self.ResPartner.search(
            [("located_in_stock_release_channel_ids", "like", "Alpha")]
        )
        self.assertIn(self.partner_a, partners)
        self.assertIn(self.partner_b, partners)
        self.assertNotIn(self.partner_c, partners)
        self.assertNotIn(self.partner_d, partners)

        partners = self.ResPartner.search(
            [("located_in_stock_release_channel_ids", "like", "Beta")]
        )
        self.assertNotIn(self.partner_a, partners)
        self.assertIn(self.partner_b, partners)
        self.assertNotIn(self.partner_c, partners)
        self.assertNotIn(self.partner_d, partners)

        partners = self.ResPartner.search(
            [("located_in_stock_release_channel_ids", "like", "Gamma")]
        )
        self.assertNotIn(self.partner_a, partners)
        self.assertNotIn(self.partner_b, partners)
        self.assertIn(self.partner_c, partners)
        self.assertNotIn(self.partner_d, partners)

        partners = self.ResPartner.search(
            [("located_in_stock_release_channel_ids", "like", "NonExistent")]
        )
        self.assertFalse(partners)

    def test_search_located_in_stock_release_channel_ids_ilike(self):
        partners = self.ResPartner.search(
            [("located_in_stock_release_channel_ids", "ilike", "alpha")]
        )
        self.assertIn(self.partner_a, partners)
        self.assertIn(self.partner_b, partners)
        self.assertNotIn(self.partner_c, partners)
        self.assertNotIn(self.partner_d, partners)

    def test_search_located_in_stock_release_channel_ids_unsupported_operator(self):
        with self.assertRaises(UserError):
            self.ResPartner.search(
                [("located_in_stock_release_channel_ids", "=", "Alpha")]
            )

    def test_search_located_in_stock_release_channel_ids_unsupported_value_type(self):
        with self.assertRaises(UserError):
            self.ResPartner.search(
                [("located_in_stock_release_channel_ids", "like", 123)]
            )

    def test_partner_with_no_channel(self):
        partners = self.ResPartner.search(
            [("located_in_stock_release_channel_ids", "like", "Alpha")]
        )
        self.assertNotIn(self.partner_d, partners)

        partners = self.ResPartner.search(
            [("located_in_stock_release_channel_ids", "like", "Gamma")]
        )
        self.assertNotIn(self.partner_d, partners)
