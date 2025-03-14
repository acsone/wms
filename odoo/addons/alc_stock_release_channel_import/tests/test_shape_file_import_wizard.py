# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64

from shapely.geometry.multipolygon import MultiPolygon
from shapely.geometry.polygon import Polygon

from odoo.modules.module import get_resource_path
from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger


class TestShapeFileImportWizard(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.wizard_model = cls.env["alc.import.delivery.zone.wizard"]
        cls.channel_model = cls.env["stock.release.channel"]
        cls.polygon = Polygon(
            [
                [3.157493, 50.776306],
                [3.157075, 50.776594],
                [3.156601, 50.777019],
                [3.156126, 50.777434],
                [3.155595, 50.777824],
            ]
        )
        cls.multipolygon = MultiPolygon([cls.polygon])
        cls.preparation_plan = cls.env.ref(
            "stock_release_channel_plan.stock_release_channel_preparation_plan_demo_mon"
        )

    def _do_import(self, shape_filename):
        shape_file_path = get_resource_path(
            "alc_stock_release_channel_import", "tests", "resources", shape_filename
        )
        with open(shape_file_path, "rb") as f:
            content = base64.encodebytes(f.read())
            values = {"file": content, "preparation_plan_id": self.preparation_plan.id}
            wizard = self.wizard_model.create(values)
            wizard.button_import()

    def test_create_channel(self):
        self._do_import("shape_test_1.zip")
        self.assertTrue(self.channel_model.search([("name", "=", "D1")]))
        self.assertTrue(self.channel_model.search([("shape_name", "=", "D1")]))

    @mute_logger("shapefile")
    def test_update_channel(self):
        """Channel 2 already exist => do update."""
        channel = self.channel_model.create(
            {"name": "D2", "preparation_plan_ids": [(6, 0, self.preparation_plan.ids)]}
        )
        self._do_import("shape_test_2.zip")
        self.assertTrue(isinstance(channel.delivery_zone, MultiPolygon))
        self.assertEqual(channel.name, "D2")

    @mute_logger("shapefile")
    def test_update_channel_2(self):
        """Channel 2 already exist => do update."""
        channel = self.channel_model.create(
            {
                "name": "xxxx",
                "shape_name": "D2",
                "preparation_plan_ids": [(6, 0, self.preparation_plan.ids)],
            }
        )
        self._do_import("shape_test_2.zip")
        self.assertTrue(isinstance(channel.delivery_zone, MultiPolygon))
        self.assertEqual(channel.name, "xxxx")
        self.assertEqual(channel.shape_name, "D2")

    @mute_logger("shapefile")
    def test_archive_channel(self):
        """
        Channel 3 does not exist but channel 1 does => delete channel 1.

        Assert D1 archived
        """
        self.channel_model.create(
            {
                "name": "D1",
                "delivery_zone": self.multipolygon,
                "preparation_plan_ids": [(6, 0, self.preparation_plan.ids)],
            }
        )
        self._do_import("shape_test_3.zip")
        self.assertFalse(self.channel_model.search([("name", "=", "D1")]))

    def test_import_multiple_channels(self):
        self.preparation_plan.release_channel_ids = False
        self.assertFalse(
            self.channel_model.search(
                [("preparation_plan_ids", "in", self.preparation_plan.ids)]
            )
        )
        self._do_import("shape_test_4.zip")
        channels = self.channel_model.search(
            [("preparation_plan_ids", "in", self.preparation_plan.ids)]
        )
        self.assertEqual(len(channels), 8)
        self.assertSetEqual(
            set(channels.mapped("name")),
            {"D13", "D1", "D4", "D20", "D16", "D2", "D7", "D12"},
        )
