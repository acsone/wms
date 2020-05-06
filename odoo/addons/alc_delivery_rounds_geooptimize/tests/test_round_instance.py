# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime
import json
import logging
from collections import deque
from contextlib import contextmanager

from requests.exceptions import HTTPError

import mock
from odoo.addons.delivery_rounds.tests import common


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
                "geo_optimization_duration": 1,
                "geo_optimization_delivery_duration": 10,
                "geo_optimization_loading_duration": 100,
            }
        ).execute()
        cls.delivery_round_1.geo_optimization_enabled = True

        cls.partner1.write({"partner_latitude": 10.1, "partner_longitude": 10.1})
        cls.partner2.write({"partner_latitude": 10.2, "partner_longitude": 10.2})
        cls.partner3.write({"partner_latitude": 10.3, "partner_longitude": 10.3})

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

        requests_get_patcher = mock.patch("requests.get")
        requests_post_patcher = mock.patch("requests.post")
        self.mocked_requests_post = requests_post_patcher.start()
        self.mocked_requests_get = requests_get_patcher.start()

        @self.addCleanup
        def stop_mock():
            requests_post_patcher.stop()
            requests_get_patcher.stop()

    def filter(self, record):
        return 0

    @contextmanager
    def api_post_optimize(self, status_code, json_result):
        self.mocked_requests_post.return_value = _PseudoRequestsResponse(
            status_code, json_result
        )
        yield
        self.mocked_requests_post.return_value = mock.MagicMock()

    @contextmanager
    def api_get_results(
        self, *results  # must be a list of tuple (status_code, json_resul)
    ):
        res = deque(results)

        def get(url, **kwargs):
            result_status_code, result_json_result = res.popleft()
            return _PseudoRequestsResponse(result_status_code, result_json_result)

        self.mocked_requests_get.side_effect = get
        yield
        self.mocked_requests_get.side_effect = mock.MagicMock()

    def _simulate_optimize(self, *partner_ids):
        """
        Simulate an optimization where the order of the partners into the
        result is the one received as args
        """
        expected_result = {
            "status": "OK",
            "plannedOrders": [{"stopId": "%s" % p.id} for p in partner_ids],
        }
        with self.api_post_optimize(
            200, {"taskId": "123", "status": "OK"}
        ), self.api_get_results(
            (200, {"status": "OK", "optimizeStatus": "terminated"}),
            (200, expected_result),
        ):
            self.delivery_round_1.button_deliver()
        self.assertEqual(self.delivery_round_1.state, "done")

    def assertJsonEqual(self, expected, value):
        expected_str = json.dumps(expected, sort_keys=True)
        value_str = json.dumps(expected, sort_keys=True)
        self.assertEqual(expected_str, value_str)

    def test_00(self):
        """
        Data:
            A round ready to be delivered
        Test case:
            Deliver and receive an exception from the optimization API
        Expected result:
            delivery.round must be in state optimization_failure
            the error message must be the http_error_message
        """
        with self.api_post_optimize(400, {}):
            self.delivery_round_1.button_deliver()
        self.assertEqual(self.delivery_round_1.state, "optimization_failure")
        self.assertEqual(
            self.delivery_round_1.geo_optimization_error_message,
            "400 Client Error: Fake reason for status code 400",
        )

    def test_01(self):
        """
        Data:
            A round ready to be delivered
        Test case:
            Deliver and receive a result with statue ERROR and an error message
            from the optimization API
        Expected result:
            delivery.round must be in state optimization_failure
            the error message must be the error message from the api response
        """
        with self.api_post_optimize(200, {"status": "ERROR", "message": "api error"}):
            self.delivery_round_1.button_deliver()
        self.assertEqual(self.delivery_round_1.state, "optimization_failure")
        self.assertEqual(
            self.delivery_round_1.geo_optimization_error_message, "api error"
        )

    def test_02(self):
        """
        Data:
            A round ready to be delivered
        Test case:
            Deliver
            Receive a result with a task id
            Receive an http exception when calling the status api
        Expected result:
            state: optimization_failure
            geo_optimization_task_id: set
            geo_optimization_error_message: the http_error_message
        """
        with self.api_post_optimize(
            200, {"taskId": "123", "status": "OK"}
        ), self.api_get_results((400, {})):
            self.delivery_round_1.button_deliver()
        self.assertEqual(self.delivery_round_1.state, "optimization_failure")
        self.assertEqual(
            self.delivery_round_1.geo_optimization_error_message,
            "400 Client Error: Fake reason for status code 400",
        )
        self.assertEqual(self.delivery_round_1.geo_optimization_task_id, "123")

    def test_03(self):
        """
        Data:
            A round ready to be delivered
        Test case:
            Deliver
            Receive a result with a task id
            Receive a result with status ERROR and an error message when
            calling the status api
        Expected result:
            state: optimization_failure
            geo_optimization_task_id: set
            geo_optimization_error_message: the error message from the api response
        """
        with self.api_post_optimize(
            200, {"taskId": "123", "status": "OK"}
        ), self.api_get_results((200, {"status": "ERROR", "message": "status error"})):
            self.delivery_round_1.button_deliver()
        self.assertEqual(self.delivery_round_1.state, "optimization_failure")
        self.assertEqual(
            self.delivery_round_1.geo_optimization_error_message, "status error"
        )
        self.assertEqual(self.delivery_round_1.geo_optimization_task_id, "123")

    def test_04(self):
        """
        Data:
            A round ready to be delivered
        Test case:
            Deliver
            Receive a result with a task id
            Receive a status ok and optimizeStatus terminated
            Receive an http exception when calling optimization result
        Expected result:
            state: optimization_failure
            geo_optimization_task_id: set
            geo_optimization_error_message: the http_error_message
        """
        with self.api_post_optimize(
            200, {"taskId": "123", "status": "OK"}
        ), self.api_get_results(
            (200, {"status": "OK", "optimizeStatus": "terminated"}), (400, {})
        ):
            self.delivery_round_1.button_deliver()
        self.assertEqual(self.delivery_round_1.state, "optimization_failure")
        self.assertEqual(
            self.delivery_round_1.geo_optimization_error_message,
            "400 Client Error: Fake reason for status code 400",
        )
        self.assertEqual(self.delivery_round_1.geo_optimization_task_id, "123")

    def test_05(self):
        """
        Data:
            A round ready to be delivered
        Test case:
            Deliver
            Receive a result with a task id
            Receive a status ok and optimizeStatus terminated
            Receive a result with status ERROR and an error message when calling optimization result
        Expected result:
            state: optimization_failure
            geo_optimization_task_id: set
            geo_optimization_error_message: the error message from the api response
        """
        with self.api_post_optimize(
            200, {"taskId": "123", "status": "OK"}
        ), self.api_get_results(
            (200, {"status": "OK", "optimizeStatus": "terminated"}),
            (200, {"status": "ERROR", "message": "result error"}),
        ):
            self.delivery_round_1.button_deliver()
        self.assertEqual(self.delivery_round_1.state, "optimization_failure")
        self.assertEqual(
            self.delivery_round_1.geo_optimization_error_message, "result error"
        )
        self.assertEqual(self.delivery_round_1.geo_optimization_task_id, "123")

    def test_06(self):
        """
        Data:
            A round ready to be delivered
        Test case:
            Deliver
            Receive a result with a task id
            Receive a status ok and optimizeStatus terminated
            Receive a result with missing partner when calling optimization result
        Expected result:
            state: optimization_failure
            geo_optimization_error_message: a validation error message
        """
        with self.api_post_optimize(
            200, {"taskId": "123", "status": "OK"}
        ), self.api_get_results(
            (200, {"status": "OK", "optimizeStatus": "terminated"}),
            (
                200,
                {
                    "status": "OK",
                    "plannedOrders": [
                        {"stopId": "%s" % self.partner1.id},
                        {"stopId": "%s" % self.partner2.id},
                    ],
                },
            ),
        ):
            self.delivery_round_1.button_deliver()
        self.assertEqual(self.delivery_round_1.state, "optimization_failure")
        self.assertEqual(
            self.delivery_round_1.geo_optimization_error_message,
            "The following partners are not found into the optimization result: %s"
            % self.partner3.name,
        )

    def test_07(self):
        """
        Data:
            A round ready to be delivered
        Test case:
            Deliver
            Receive a result with a task id
            Receive a status ok and optimizeStatus terminated
            Receive a result with unexpected partner when calling optimization result
        Expected result:
            state: optimization_failure
            geo_optimization_error_message: a validation error message
        """
        with self.api_post_optimize(
            200, {"taskId": "123", "status": "OK"}
        ), self.api_get_results(
            (200, {"status": "OK", "optimizeStatus": "terminated"}),
            (
                200,
                {
                    "status": "OK",
                    "plannedOrders": [
                        {"stopId": "%s" % self.partner1.id},
                        {"stopId": "%s" % self.partner2.id},
                        {"stopId": "%s" % self.partner3.id},
                        {"stopId": "4"},
                        {"stopId": "5"},
                    ],
                },
            ),
        ):
            self.delivery_round_1.button_deliver()
        self.assertEqual(self.delivery_round_1.state, "optimization_failure")
        self.assertEqual(
            self.delivery_round_1.geo_optimization_error_message,
            "The following partner ids are not expected into the "
            "optimization result: 4, 5",
        )

    def test_08(self):
        """
        Data:
            A round ready to be delivered
        Test case:
            Deliver
            Receive a result with a task id
            Receive a status ok and optimizeStatus terminated
            Receive a result with the required infos
        Expected result:
            state: done
            geo_optimization_json contains the result received from the api
        """
        expected_result = {
            "status": "OK",
            "plannedOrders": [
                {"stopId": "%s" % self.partner2.id},
                {"stopId": "%s" % self.partner1.id},
                {"stopId": "%s" % self.partner3.id},
            ],
        }
        with self.api_post_optimize(
            200, {"taskId": "123", "status": "OK"}
        ), self.api_get_results(
            (200, {"status": "OK", "optimizeStatus": "terminated"}),
            (200, expected_result),
        ):
            self.delivery_round_1.button_deliver()
        self.assertEqual(self.delivery_round_1.state, "done")
        self.assertDictEqual(
            self.delivery_round_1.geo_optimization_json, expected_result
        )

    def test_09(self):
        """
        Data:
            A delivery round optimized with partners in the following order:
            p3, p1, p2
        Test case:
            Call _get_sorted_shipping_ids
            Do a new optimization with order p2, p1, p3
            Call _get_sorted_shipping_ids
        Expected result:
            Result of call to _get_sorted_shipping_ids is ordered into the
            same order as the order into the optimization result

        """
        self._simulate_optimize(self.partner3, self.partner1, self.partner2)
        shippings = self.delivery_round_1._get_sorted_shipping_ids()
        self.assertEqual(shippings[0].partner_id, self.partner3)
        self.assertEqual(shippings[1].partner_id, self.partner1)
        self.assertEqual(shippings[2].partner_id, self.partner2)
        self._simulate_optimize(self.partner2, self.partner1, self.partner3)
        shippings = self.delivery_round_1._get_sorted_shipping_ids()
        self.assertEqual(shippings[0].partner_id, self.partner2)
        self.assertEqual(shippings[1].partner_id, self.partner1)
        self.assertEqual(shippings[2].partner_id, self.partner3)

    def test_10(self):
        """
        Data:
            A round ready to be delivered for 3 partners
        Test case:
            Call method _generate_optimization_request
        Expected result:
            The json is conform to what's expected
        """
        res = self.delivery_round_1._generate_optimization_request()
        self.maxDiff = 2000
        shippings = self.delivery_round_1.shipping_ids
        expected = {
            "depots": [{"x": 0.0, "y": 0.0}],
            "language": u"en_US",
            "options": {
                "maxOptimDuration": "00:00:01",
                "vehicleCode": "deliveryIntermediateVehicle",
            },
            "orders": [
                {
                    "customerId": shippings[0].partner_id.id,
                    "fixedVisitDuration": "00:00:10",
                    "id": shippings[0].partner_id.id,
                    "label": shippings[0].partner_id.name,
                    "phone": "",
                    "type": 0,
                    "x": shippings[0].partner_id.partner_longitude,
                    "y": shippings[0].partner_id.partner_latitude,
                },
                {
                    "customerId": shippings[1].partner_id.id,
                    "fixedVisitDuration": "00:00:10",
                    "id": shippings[1].partner_id.id,
                    "label": shippings[1].partner_id.name,
                    "phone": "",
                    "type": 0,
                    "x": shippings[1].partner_id.partner_longitude,
                    "y": shippings[1].partner_id.partner_latitude,
                },
                {
                    "customerId": shippings[2].partner_id.id,
                    "fixedVisitDuration": "00:00:10",
                    "id": shippings[2].partner_id.id,
                    "label": shippings[2].partner_id.name,
                    "phone": "",
                    "type": 0,
                    "x": shippings[2].partner_id.partner_longitude,
                    "y": shippings[2].partner_id.partner_latitude,
                },
            ],
            "resources": [
                {
                    "endX": 0.0,
                    "endY": 0.0,
                    "fixedLoadingDuration": "01:40:00",
                    "loadBeforeDeparture": True,
                    "noReload": True,
                    "openStart": False,
                    "startX": 0.0,
                    "startY": 0.0,
                    "workStartTime": "00:00:00",
                }
            ],
            "simulationName": self.delivery_round_1.display_name,
        }
        self.assertJsonEqual(res, expected)

    def test_11(self):
        """
        Data:
            A round ready to be delivered for 3 partners
        Test case:
            Add 2 delivery windows on partner1 for current day
            Add 2 delivery windows on partner2 for tomorrow
            Call method _generate_optimization_request

        Expected result:
            The json is conform to what's expected (only contains time windows
            for partner1)
        """
        today = datetime.datetime.today()
        week_day_today = today.weekday()
        week_day_tomorrow = (today + datetime.timedelta(days=1)).weekday()
        AlcDeliveryWeekDay = self.env["alc.delivery.week.day"]
        AlcDeliveryWindow = self.env["alc.delivery.window"]
        today_id = AlcDeliveryWeekDay._get_id_by_name("%s" % week_day_today)
        tomorrow_id = AlcDeliveryWeekDay._get_id_by_name("%s" % week_day_tomorrow)
        AlcDeliveryWindow.create(
            {
                "partner_id": self.partner1.id,
                "week_day_ids": [(4, today_id)],
                "start": 16.0,
                "end": 18.0,
            }
        )
        AlcDeliveryWindow.create(
            {
                "partner_id": self.partner1.id,
                "week_day_ids": [(4, today_id)],
                "start": 10.0,
                "end": 12.0,
            }
        )
        AlcDeliveryWindow.create(
            {
                "partner_id": self.partner2.id,
                "week_day_ids": [(4, tomorrow_id)],
                "start": 11.0,
                "end": 13.0,
            }
        )
        AlcDeliveryWindow.create(
            {
                "partner_id": self.partner2.id,
                "week_day_ids": [(4, tomorrow_id)],
                "start": 15.0,
                "end": 17.0,
            }
        )
        cfg = self.delivery_round_1.get_optimization_config()
        res = {
            c["customerId"]: c
            for c in self.delivery_round_1._generate_optimization_orders(cfg)
        }
        for partner_id, result in res.items():
            partner = self.env["res.partner"].browse(partner_id)
            expected = {
                "customerId": partner.id,
                "fixedVisitDuration": "00:00:10",
                "id": partner.id,
                "label": partner.name,
                "phone": "",
                "type": 0,
                "x": partner.partner_longitude,
                "y": partner.partner_latitude,
            }
            if partner_id == self.partner1.id:
                expected["timeWindows"] = [
                    {"beginTime": "10:00", "endTime": "12:00"},
                    {"beginTime": "16:00", "endTime": "18:00"},
                ]

            self.assertJsonEqual(expected, result)

    def test_12(self):
        """
        Data:
            A round ready to be delivered
        Test case:
            1 Deliver and receive an exception from the optimization API
            2 Call button_ignore_optimization_failure
        Expected result:
            1 delivery.round must be in state optimization_failure
            2 delivery.round must be in state done
        """
        with self.api_post_optimize(400, {}):
            self.delivery_round_1.button_deliver()
        self.assertEqual(self.delivery_round_1.state, "optimization_failure")
        self.delivery_round_1.button_ignore_optimization_failure()
        self.assertEqual(self.delivery_round_1.state, "done")

    def test_13(self):
        """
        Data:
            A round ready to be delivered
        Test case:
            1 Deliver and receive an exception from the optimization API
            2 Call retry_optimization and Receive a result with the required infos
        Expected result:
            1 delivery.round must be in state optimization_failure
            2 delivery.round must be in state done
        """
        with self.api_post_optimize(400, {}):
            self.delivery_round_1.button_deliver()
        self.assertEqual(self.delivery_round_1.state, "optimization_failure")
        self.delivery_round_1.button_ignore_optimization_failure()
        expected_result = {
            "status": "OK",
            "plannedOrders": [
                {"stopId": "%s" % self.partner2.id},
                {"stopId": "%s" % self.partner1.id},
                {"stopId": "%s" % self.partner3.id},
            ],
        }
        with self.api_post_optimize(
            200, {"taskId": "123", "status": "OK"}
        ), self.api_get_results(
            (200, {"status": "OK", "optimizeStatus": "terminated"}),
            (200, expected_result),
        ):
            self.delivery_round_1.retry_optimization()
        self.assertEqual(self.delivery_round_1.state, "done")

    def test_14(self):
        """
        Data:
            An api url with subpath
        Test case:
            call _get_optimization_url
        Expected result:
            subpath is preserved
        """
        self.StockConfigSettings.create(
            {
                "geo_optimization_api_url": "https://geoservices.geoconcept.com/"
                "ToursolverCloud/api/ts/toursolver/"
            }
        ).execute()
        url = self.delivery_round_1._get_opitization_api_url("test")
        self.assertEqual(
            url,
            "https://geoservices.geoconcept.com/ToursolverCloud/api/ts/"
            "toursolver/test?tsCloudApiKey=api+key",
        )
        url = self.delivery_round_1._get_opitization_api_url("test", param1="val2")
        self.assertEqual(
            url,
            "https://geoservices.geoconcept.com/ToursolverCloud/api/ts/"
            "toursolver/test?tsCloudApiKey=api+key&param1=val2",
        )

    def test_15(self):
        """
           Data:
               A round ready to be delivered
           Test case:
               Deliver
               Receive a result with a task id
               Recieve a status ok and optimizeStatus running
               Receive a status ok and optimizeStatus terminated
               Receive a result with the required infos
           Expected result:
               state: done
               geo_optimization_json contains the result received from the api
           """
        expected_result = {
            "status": "OK",
            "plannedOrders": [
                {"stopId": "%s" % self.partner2.id},
                {"stopId": "%s" % self.partner1.id},
                {"stopId": "%s" % self.partner3.id},
            ],
        }
        with self.api_post_optimize(
            200, {"taskId": "123", "status": "OK"}
        ), self.api_get_results(
            (200, {"status": "OK", "optimizeStatus": "running"}),
            (200, {"status": "OK", "optimizeStatus": "terminated"}),
            (200, expected_result),
        ):
            self.delivery_round_1.button_deliver()
        self.assertEqual(self.delivery_round_1.state, "done")

        self.assertDictEqual(
            self.delivery_round_1.geo_optimization_json, expected_result
        )

    def test_16(self):
        """
        Data:
            A round for 3 partners ready to be delivered for 2 partners 'pick1 not done'
        Test case:
             Call method _generate_optimization_request
        Expected result:
            Only partners for pick2 and pick3 must be into the genreated json
        """
        self.pick1.move_lines.write({"state": "assigned"})
        cfg = self.delivery_round_1.get_optimization_config()
        res = {
            c["customerId"]
            for c in self.delivery_round_1._generate_optimization_orders(cfg)
        }
        expected = {self.partner2.id, self.partner3.id}
        self.assertEqual(res, expected)


class _PseudoRequestsResponse(object):
    def __init__(self, status_code, json_result):
        self.status_code = status_code
        self.json_result = json_result
        self.reason = "Fake reason for status code %s" % self.status_code

    def json(self):
        return self.json_result

    def raise_for_status(self):
        http_error_msg = ""
        if 400 <= self.status_code < 500:
            http_error_msg = u"%s Client Error: %s" % (self.status_code, self.reason)

        elif 500 <= self.status_code < 600:
            http_error_msg = u"%s Server Error: %s" % (self.status_code, self.reason)

        if http_error_msg:
            raise HTTPError(http_error_msg, response=self)
