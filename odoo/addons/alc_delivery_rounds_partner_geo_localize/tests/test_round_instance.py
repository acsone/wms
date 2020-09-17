# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


import json
import logging

import responses
from freezegun import freeze_time
from odoo.addons.delivery_rounds.tests import common
from odoo.exceptions import ValidationError


class TestRoundInstance(common.DeliveryRoundTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestRoundInstance, cls).setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context, test_queue_job_no_delay=True, mail_notrack=True
            )
        )
        cls.delivery_round_1 = cls.delivery_round_1.with_context(cls.env.context)
        cls.StockConfigSettings = cls.env["stock.config.settings"]
        cls.StockConfigSettings.create(
            {
                "geo_optimization_enabled": True,
                "geo_optimization_api_url": "my_url",
                "geo_optimization_api_key": "api key",
                "geo_optimization_duration": 90,
                "geo_optimization_delivery_duration": 10,
                "geo_optimization_loading_duration": 100,
                "geo_optimization_resources_number": 1,
            }
        ).execute()
        cls.delivery_round_1.write(
            {"geo_optimization_enabled": True, "geo_optimization_resource_id": "D1"}
        )
        cls.partner1.write({"partner_latitude": 10.1, "partner_longitude": 10.1})

        vals = {
            "name": "Partner Project",
            "street": "Rue bois des noix",
            "country_id": cls.env.ref("base.be").id,
            "zip": "5060",
            "city": "Tamines",
        }
        cls.partner2.write(vals)

        vals2 = {
            "name": "Partner 2 Project",
            "street": "Rue du polisart",
            "country_id": cls.env.ref("base.be").id,
            "zip": "5300",
            "city": "Andenne",
        }

        cls.partner3.write(vals2)

        # makes all the pickings done into the for the round...
        pick1 = cls._create_picking_pick(partner=cls.partner1)
        pick2 = cls._create_picking_pick(partner=cls.partner2)
        pick3 = cls._create_picking_pick(partner=cls.partner3)

        ship1 = cls._create_picking_out(cls.partner1)
        ship2 = cls._create_picking_out(cls.partner2)
        ship3 = cls._create_picking_out(cls.partner3)

        # we don't care about the details if it is really
        # in that state, we force the state to assigned to be sure that
        # these pickings will be linked to the delivery round
        pick1.move_lines.write({"state": "assigned"})
        pick2.move_lines.write({"state": "assigned"})
        pick3.move_lines.write({"state": "assigned"})

        ship1.move_lines.write({"state": "assigned"})
        ship2.move_lines.write({"state": "assigned"})
        ship3.move_lines.write({"state": "assigned"})

        pickings = pick1 | pick2 | pick3 | ship1 | ship2 | ship3
        cls.delivery_round_1._assign_pickings(pickings)

        # we don't care about the details if it is really
        # in that state, it is only for the round to think it is
        pick1.move_lines.write({"state": "done"})
        pick2.move_lines.write({"state": "done"})
        pick3.move_lines.write({"state": "done"})
        # at this stage we have a round ready to be delivered

        cls.pick1 = pick1

    def setUp(self):
        super(TestRoundInstance, self).setUp()

        # mute logger
        loggers = [
            "odoo.addons.alc_delivery_rounds_geooptimize.models.round_instance",
            "odoo.addons.queue_job.models.base",
        ]
        for logger in loggers:
            logging.getLogger(logger).addFilter(self)

        @self.addCleanup
        def un_mute_logger():
            for logger_ in loggers:
                logging.getLogger(logger_).removeFilter(self)

    def filter(self, record):
        return 0

    def assertJsonEqual(self, expected, value):
        expected_str = json.dumps(expected, sort_keys=True)
        value_str = json.dumps(value, sort_keys=True)
        self.assertEqual(expected_str, value_str)

    @responses.activate
    def test_00(self):
        """ Check that geolocalize is working properly"""
        responses.add(
            responses.Response(
                method="GET",
                url="https://nominatim.openstreetmap.org/search?"
                + "city=Tamines&format=json&country=Belgium&"
                + "state=&street=Rue+bois+des+noix&limit=1&postalCode=5060",
                match_querystring=True,
                json=[{"lat": 50.4311411, "lon": 4.6132813}],
                status=200,
            )
        )

        self.partner2.geo_localize()

        # Geolocalize has another context : need to force refresh to see the changes in current context
        self.partner2.refresh()

        self.assertEqual(len(responses.calls), 1, "call does not exist")
        self.assertAlmostEqual(
            self.partner2.partner_latitude, 50.4311411, 3, "Latitude Should be equals"
        )
        self.assertAlmostEqual(
            self.partner2.partner_longitude, 4.6132813, 3, "Longitude Should be equals"
        )

    @responses.activate
    @freeze_time("2020-01-01 07:10:00")
    def test_01(self):
        """
        Data:
            A round ready to be delivered for 3 partners.
            Partner 3 has an address but no coordinates => needs to recompute
        Test case:
            Call method _generate_optimization_request
        Expected result:
            The json is conform to what's expected
        """

        # Set latitude and longitude on partner 2
        self.partner2.write({"partner_latitude": 10.2, "partner_longitude": 10.2})

        responses.add(
            responses.Response(
                method="GET",
                url="https://nominatim.openstreetmap.org/search?"
                + "city=Andenne&format=json&country=Belgium&"
                + "state=&street=Rue+du+polisart&limit=1&postalCode=5300",
                match_querystring=True,
                json=[{"lat": 50.5114237, "lon": 5.0840081}],
                status=200,
            )
        )

        res = self.delivery_round_1._generate_optimization_request()
        partner_ids = self.delivery_round_1.shipping_ids.mapped("partner_id.id")
        partner_ids.sort()
        partners = self.env["res.partner"].browse(partner_ids)

        # Check that partner 3 got a localization after the optimization request
        self.assertAlmostEqual(
            self.partner3.partner_latitude, 50.5114237, 3, "Latitude Should be equals"
        )
        self.assertAlmostEqual(
            self.partner3.partner_longitude, 5.0840081, 3, "Longitude Should be equals"
        )

        expected = {
            "beginDate": "2017-01-01",
            "countryCode": "BE",
            "depots": [{"id": "dep_1", "x": 5.2758074, "y": 50.5825464}],
            "language": u"en_US",
            "options": {
                "maxOptimDuration": "00:01:30",
                "vehicleCode": "deliveryIntermediateVehicle",
            },
            "orders": [
                {
                    "customerId": partners[0].ref,
                    "fixedVisitDuration": "00:00:10",
                    "id": partners[0].id,
                    "label": partners[0].name,
                    "phone": "",
                    "type": 0,
                    "x": partners[0].partner_longitude,
                    "y": partners[0].partner_latitude,
                },
                {
                    "customerId": partners[1].ref,
                    "customDataMap": {"address": partners[1].contact_address},
                    "fixedVisitDuration": "00:00:10",
                    "id": partners[1].id,
                    "label": partners[1].name,
                    "phone": "",
                    "type": 0,
                    "x": partners[1].partner_longitude,
                    "y": partners[1].partner_latitude,
                },
                {
                    "customerId": partners[2].ref,
                    "customDataMap": {"address": partners[2].contact_address},
                    "fixedVisitDuration": "00:00:10",
                    "id": partners[2].id,
                    "label": partners[2].name,
                    "phone": "",
                    "type": 0,
                    "x": partners[2].partner_longitude,
                    "y": partners[2].partner_latitude,
                },
            ],
            "resources": [
                {
                    "endX": 5.2758074,
                    "endY": 50.5825464,
                    "fixedLoadingDuration": "01:40:00",
                    "globalCapacity": 9999,
                    "id": "D1",
                    "loadBeforeDeparture": True,
                    "mobileLogin": "d1@alcyonbelux.be",
                    "noReload": True,
                    "openStart": False,
                    "startX": 5.2758074,
                    "startY": 50.5825464,
                    "useAllCapacities": False,
                    "workStartTime": "08:11:00",
                }
            ],
            "simulationName": self.delivery_round_1.display_name,
        }
        self.assertJsonEqual(res, expected)

    @responses.activate
    @freeze_time("2020-01-01 07:10:00")
    def test_02(self):
        """
        Data:
            A round ready to be delivered for 3 partners.
            Partner 1 has an invalid address  and no coordinates => should raise an error
        Test case:
            Call method _generate_optimization_request
        """

        # Set latitude and longitude on partner 2
        self.partner2.write({"partner_latitude": 10.2, "partner_longitude": 10.2})
        self.partner3.write({"partner_latitude": 10.3, "partner_longitude": 10.3})
        self.partner1.write({"partner_latitude": False, "partner_longitude": False})
        # Set an unexisting address on partner3 so that osm cannot localize the partner. Should raise an error
        vals3 = {
            "street": "Rue test",
            "city": "Tmnss",
            "country_id": self.env.ref("base.be").id,
        }
        self.partner1.write(vals3)
        # OSM tries 2 times to localize the partner
        responses.add(
            responses.Response(
                method="GET",
                url="https://nominatim.openstreetmap.org/search?city=Tmnss&"
                + "format=json&country=Belgium&state=&street=Rue+test&"
                + "limit=1&postalCode=",
                match_querystring=True,
                json=[{}],
            )
        )

        responses.add(
            responses.Response(
                method="GET",
                url="https://nominatim.openstreetmap.org/search?city=Tmnss&"
                + "format=json&country=Belgium&state=&street=&"
                + "limit=1&postalCode=",
                match_querystring=True,
                json=[{}],
            )
        )

        # Check that partner 1 is not localized
        with self.assertRaises(ValidationError):
            self.delivery_round_1._generate_optimization_request()

        self.assertFalse(self.partner1.partner_longitude)
        self.assertFalse(self.partner1.partner_latitude)
