# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SV/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from shapely.geometry.multipolygon import MultiPolygon
from shapely.geometry.polygon import Point, Polygon

from odoo.tests.common import TransactionCase


class TestComputeRoundTemplateIds(TransactionCase):
    def setUp(self):
        super(TestComputeRoundTemplateIds, self).setUp()
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

        self.round_template1 = self.env["round.template"].create(
            {"name": "testing in template 1", "geo_polygon_shape": multipolygon}
        )

        self.round_template2 = self.env["round.template"].create(
            {"name": "testing in template 2", "geo_polygon_shape": multipolygon}
        )
        point1 = Point([4.602541, 50.435587])

        self.partner = self.env["res.partner"].create(
            {"name": "test compute", "geo_point": point1}
        )

    def test_1(self):
        self.partner._compute_round_template_ids()

        self.assertIn(self.round_template1.id, self.partner.round_template_ids.ids)
        self.assertIn(self.round_template2.id, self.partner.round_template_ids.ids)
