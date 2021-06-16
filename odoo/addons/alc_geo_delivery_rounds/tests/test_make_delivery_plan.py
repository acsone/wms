# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from shapely.geometry.multipolygon import MultiPolygon
from shapely.geometry.polygon import Point, Polygon

from odoo.addons.delivery_rounds.tests import common


class TestMakeDeliveryPlanWizard(common.DeliveryRoundTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestMakeDeliveryPlanWizard, cls).setUpClass()

        cls.env = cls.env(context=dict(cls.env.context, test_queue_job_no_delay=True))

        cls.warehouse_1.pick_type_id.subcode = "PICK"

        cls.delivery_round_1 = cls.delivery_round_1.with_context(cls.env.context)

        cls.tag_monday = cls.env["round.tag"].create({"name": "Monday"})

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
        cls.delivery_template_polygon = cls.env["round.template"].create(
            {
                "name": "Unittest delivery template 2",
                "geo_polygon_shape": multipolygon,
                "time_picking_planned": 8,
                "time_leave_planned": 9,
                "tag_ids": [(4, cls.tag_monday.id)],
            }
        )
        cls.delivery_template.write(
            {
                "time_picking_planned": 8,
                "time_leave_planned": 9,
                "tag_ids": [(4, cls.tag_monday.id)],
            }
        )

        cls.version = cls.env["round.template.version"].create(
            {
                "name": "Morning",
                "template_ids": [
                    (6, 0, [cls.delivery_template.id, cls.delivery_template_polygon.id])
                ],
            }
        )

        point1 = Point([4.602541, 50.435587])
        point3 = Point([4.606292, 50.436579])

        cls.partner1.write(
            {
                "name": "partner to deliver",
                "geo_point": point1,
                "tag_ids": [(6, 0, [cls.tag_monday.id])],
            }
        )
        cls.partner3.write(
            {
                "name": "partner to deliver too",
                "geo_point": point3,
                "tag_ids": [(6, 0, [cls.tag_monday.id])],
            }
        )

        cls.partner2.write(
            {
                "name": "partner to deliver fixed",
                "tag_ids": [(6, 0, [cls.tag_monday.id])],
            }
        )
        cls.pick1 = cls._create_picking_pick(partner=cls.partner1)
        cls.pick2 = cls._create_picking_pick(partner=cls.partner2)
        cls.pick3 = cls._create_picking_pick(partner=cls.partner3)

    def setUp(self):
        super(TestMakeDeliveryPlanWizard, self).setUp()
        self.MakeDeliveryPlanWizard = self.env["round.wizard.makeplan"]

        loggers = ["odoo.addons.queue_job.models.base"]
        for logger in loggers:
            logging.getLogger(logger).addFilter(self)

        # pylint: disable=unused-variable
        @self.addCleanup
        def un_mute_logger():
            for logger_ in loggers:
                logging.getLogger(logger_).removeFilter(self)

    def filter(self, record):
        return 0

    def test_make_plan(self):
        wizard = self.MakeDeliveryPlanWizard.create(
            {
                "version_id": self.version.id,
                "tag_ids": [(6, 0, [self.tag_monday.id])],
                "execution_date": "2020-07-06",
            }
        )
        wizard.confirm()

        created_delivery_round = self.env["round.instance"].search(
            [
                ("template_id", "=", self.delivery_template.id),
                ("date", "=", "2020-07-06"),
            ]
        )

        created_delivery_round2 = self.env["round.instance"].search(
            [
                ("template_id", "=", self.delivery_template_polygon.id),
                ("date", "=", "2020-07-06"),
            ]
        )

        self.assertTrue(created_delivery_round)
        self.assertTrue(created_delivery_round2)
