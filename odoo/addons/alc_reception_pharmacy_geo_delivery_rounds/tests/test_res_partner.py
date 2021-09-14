# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SV/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from shapely.geometry.multipolygon import MultiPolygon
from shapely.geometry.polygon import Point, Polygon

from odoo.addons.alc_reception_pharmacy.tests.common import CommonReceptionPharmacyCase


class TestResPartner(CommonReceptionPharmacyCase):
    @classmethod
    def setUpClass(cls):
        super(TestResPartner, cls).setUpClass()
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

        cls.round_template_dyn_1 = cls.env["round.template"].create(
            {"name": "testing in template 1", "geo_polygon_shape": multipolygon}
        )

        cls.round_template_dyn_2 = cls.env["round.template"].create(
            {"name": "testing in template 2", "geo_polygon_shape": multipolygon}
        )

    def _assign_geo_delivery(self):
        point1 = Point([4.602541, 50.435587])
        self.partner.geo_point = point1

    def test_is_delivered_by_alcyon(self):
        """
        A customer is delivered by alcyon if it's linked to an itinerary and do not use
        the optimization process or if it's part of a dynamic template..
        """
        self.assertFalse(self.partner.not_in_dynamic_delivery_round)
        self.assertFalse(self.partner.is_delivered_by_alcyon)
        self.partner.not_in_dynamic_delivery_round = True
        self.assertTrue(self.partner.is_delivered_by_alcyon)
        self.partner.not_in_dynamic_delivery_round = False
        self.assertFalse(self.partner.is_delivered_by_alcyon)
        self._assign_geo_delivery()
        self.assertTrue(self.partner.is_delivered_by_alcyon)
