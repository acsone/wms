# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from shapely.geometry.multipolygon import MultiPolygon
from shapely.geometry.polygon import Point, Polygon

from odoo.addons.delivery_rounds.tests import common


class TestMakeItineraryPlanWizard(common.DeliveryRoundTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestMakeItineraryPlanWizard, cls).setUpClass()

        cls.env = cls.env(context=dict(cls.env.context, test_queue_job_no_delay=True))

        cls.warehouse_1.pick_type_id.subcode = "PICK"

        cls.delivery_round_1 = cls.delivery_round_1.with_context(cls.env.context)

        round_tag = cls.env["round.tag"]
        cls.tag_monday = round_tag.create({"name": "Monday"})
        cls.tag_tuesday = round_tag.create({"name": "Tuesday"})
        cls.tag_wednesday = round_tag.create({"name": "Wednesday"})
        cls.tag_thursday = round_tag.create({"name": "Thursday"})
        cls.tag_friday = round_tag.create({"name": "Friday"})

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

        cls.delivery_template.write(
            {
                "geo_polygon_shape": multipolygon,
                "time_picking_planned": 8,
                "time_leave_planned": 9,
            }
        )

        cls.delivery_plan = cls.env["delivery.plan"].create(
            {"name": "test", "round_template_ids": [(4, cls.delivery_template.id)]}
        )

        point1 = Point([4.602541, 50.435587])
        point2 = Point([3.456126, 49.777434])
        point3 = Point([4.606292, 50.436579])
        point4 = Point([4.606483, 50.433348])

        cls.partner1.write(
            {
                "name": "partner to deliver",
                "geo_point": point1,
                "tag_ids": [(6, 0, [cls.tag_monday.id, cls.tag_wednesday.id])],
            }
        )
        cls.partner2.write(
            {
                "name": "no delivery",
                "geo_point": point2,
                "tag_ids": [
                    (6, 0, [cls.tag_tuesday.id, cls.tag_thursday.id, cls.tag_friday.id])
                ],
            }
        )
        cls.partner3.write(
            {
                "name": "partner to deliver too",
                "geo_point": point3,
                "tag_ids": [(6, 0, [cls.tag_monday.id, cls.tag_thursday.id])],
            }
        )

        cls.partner4 = cls.env["res.partner"].create(
            {"name": "partner to deliver without tag", "geo_point": point4}
        )

        cls.pick1 = cls._create_picking_pick(partner=cls.partner1)
        cls.pick2 = cls._create_picking_pick(partner=cls.partner2)
        cls.pick3 = cls._create_picking_pick(partner=cls.partner3)
        cls.pick4 = cls._create_picking_pick(partner=cls.partner4)

    def setUp(self):
        super(TestMakeItineraryPlanWizard, self).setUp()
        self.MakeItineraryPlanWizard = self.env["make.itinerary.plan.wizard"]

        loggers = ["odoo.addons.queue_job.models.base"]
        for logger in loggers:
            logging.getLogger(logger).addFilter(self)

        @self.addCleanup
        def un_mute_logger():
            for logger_ in loggers:
                logging.getLogger(logger_).removeFilter(self)

    def filter(self, record):
        return 0

    def test_in_polygon(self):
        self.assertTrue(
            self.delivery_template.geo_polygon_shape.contains(self.partner1.geo_point)
        )
        self.assertFalse(
            self.delivery_template.geo_polygon_shape.contains(self.partner2.geo_point)
        )

    def test_make_plan(self):
        wizard = self.MakeItineraryPlanWizard.create(
            {
                "delivery_plan_id": self.delivery_plan.id,
                "tag_ids": [(6, 0, [self.tag_monday.id])],
                "execution_date": "2020-07-06",
            }
        )
        wizard.confirm()

        # Check that the only selected picking is the one in the geoshape
        # Should be a round_instance for partner1 but not for partner2
        partners_to_deliver_name = [
            "partner to deliver",
            "partner to deliver too",
            "partner to deliver without tag",
        ]
        partner_to_exclude_name = "no delivery"
        created_delivery_round = self.env["round.instance"].search(
            [
                ("template_id", "=", self.delivery_template.id),
                ("date", "=", "2020-07-06"),
            ]
        )

        for picking in created_delivery_round.picking_ids:
            self.assertIn(picking.partner_id.name, partners_to_deliver_name)
            self.assertIsNot(picking.partner_id.name, partner_to_exclude_name)
