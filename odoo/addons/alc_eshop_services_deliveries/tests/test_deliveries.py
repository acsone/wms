# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import pytz

from odoo.fields import Datetime

from .common import TestDeliveriesService


class TestDocumentsServiceFlow(TestDeliveriesService):
    def test_search_done_records(self):
        with self.service() as service:
            done = service._search_done()
            self.assertEqual(done, self.picking_done + self.picking_half)

    def test_search_canceled_records(self):
        with self.service() as service:
            canceled = service._search_canceled()
            self.assertEqual(canceled, self.picking_cancel + self.picking_half)

    def test_search_canceled(self):
        with self.service() as service:
            result = service.dispatch("search_canceled", params={})
            self.assertEqual(len(result["data"]), 2)
            # TODO: this is the result, but this is clearly wrong...
            # self.assertEqual(result["size"], 3)

    def test_search_done(self):
        with self.service() as service:
            result = service.dispatch("search_done", params={})
            self.assertEqual(result["size"], 2)
            utc = pytz.timezone("UTC")
            expected = [
                {
                    "date": Datetime.from_string(self.picking_done.date).replace(
                        tzinfo=utc
                    ),
                    "date_done": Datetime.from_string(
                        self.picking_done.date_done
                    ).replace(tzinfo=utc),
                    "id": self.picking_done.id,
                    "move_lines": [
                        {
                            "lots": [],
                            "name": u"Shipit 1",
                            "prix_brut_htva": 0.0,
                            "prix_net_htva": 0.0,
                            "qty_ordered": 1.0,
                            "reference": u"SHP",
                            "remaining_qty": 0.0,
                            "serial_number": None,
                            "state": u"done",
                        }
                    ],
                    "name": self.picking_done.name,
                },
                {
                    "date": Datetime.from_string(self.picking_half.date).replace(
                        tzinfo=utc
                    ),
                    "date_done": Datetime.from_string(
                        self.picking_half.date_done
                    ).replace(tzinfo=utc),
                    "id": self.picking_half.id,
                    "move_lines": [
                        {
                            "lots": [],
                            "name": u"Cancel 1",
                            "prix_brut_htva": 0.0,
                            "prix_net_htva": 0.0,
                            "qty_ordered": 1.0,
                            "reference": u"CNL",
                            "remaining_qty": 1.0,
                            "serial_number": None,
                            "state": u"cancel",
                        },
                        {
                            "lots": [],
                            "name": u"Shipit 1",
                            "prix_brut_htva": 0.0,
                            "prix_net_htva": 0.0,
                            "qty_ordered": 1.0,
                            "reference": u"SHP",
                            "remaining_qty": 0.0,
                            "serial_number": None,
                            "state": u"done",
                        },
                    ],
                    "name": self.picking_half.name,
                },
            ]
            # ignore order for equality
            self.assertEqual(len(result["data"]), len(expected))
            self.assertTrue(all(r in expected for r in result["data"]))
