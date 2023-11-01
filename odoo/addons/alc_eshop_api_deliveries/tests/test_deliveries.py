# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import pytz

from .common import TestDeliveriesService


class TestDocumentsServiceFlow(TestDeliveriesService):
    def test_search_done_records(self):
        with self._create_test_client(partner=self.partner) as test_client:
            response = test_client.get("/deliveries/done")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json()["data"]), 2)
            ids = [r["id"] for r in response.json()["data"]]
            self.assertSetEqual({self.picking_done.id, self.picking_half.id}, set(ids))

    def test_search_canceled_records(self):
        with self._create_test_client(partner=self.partner) as test_client:
            response = test_client.get("/deliveries/canceled")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json()["data"]), 2)
            ids = [r["id"] for r in response.json()["data"]]
            self.assertSetEqual(
                {self.picking_cancel.id, self.picking_half.id}, set(ids)
            )

    def test_search_done(self):
        with self._create_test_client(partner=self.partner) as test_client:
            response = test_client.get("/deliveries/done")
            self.assertEqual(response.status_code, 200)
            result = response.json()
            self.assertEqual(result["size"], 2)
            pytz.timezone("UTC")
            expected = [
                {
                    "date": self.picking_done.date.isoformat() + "Z",
                    "date_done": self.picking_done.date_done.isoformat() + "Z",
                    "id": self.picking_done.id,
                    "move_lines": [
                        {
                            "lots": [],
                            "name": "Shipit 1",
                            "prix_brut_htva": 0.0,
                            "prix_net_htva": 0.0,
                            "qty_ordered": 1.0,
                            "reference": "SHP",
                            "remaining_qty": 0.0,
                            "suite": "",
                            "state": "done",
                        }
                    ],
                    "name": self.picking_done.name,
                    "partner": {
                        "city": None,
                        "street": None,
                        "name": "Partner",
                        "country": None,
                    },
                },
                {
                    "date": self.picking_half.date.isoformat() + "Z",
                    "date_done": self.picking_half.date_done.isoformat() + "Z",
                    "id": self.picking_half.id,
                    "move_lines": [
                        {
                            "lots": [],
                            "name": "Cancel 1",
                            "prix_brut_htva": 0.0,
                            "prix_net_htva": 0.0,
                            "qty_ordered": 1.0,
                            "reference": "CNL",
                            "remaining_qty": 1.0,
                            "suite": "",
                            "state": "cancel",
                        },
                        {
                            "lots": [],
                            "name": "Shipit 1",
                            "prix_brut_htva": 0.0,
                            "prix_net_htva": 0.0,
                            "qty_ordered": 1.0,
                            "reference": "SHP",
                            "remaining_qty": 0.0,
                            "suite": "",
                            "state": "done",
                        },
                    ],
                    "name": self.picking_half.name,
                    "partner": {
                        "city": None,
                        "street": None,
                        "name": "Partner",
                        "country": None,
                    },
                },
            ]
            # ignore order for equality
            self.assertEqual(len(result["data"]), len(expected))
            self.assertTrue(all(r in expected for r in result["data"]))
