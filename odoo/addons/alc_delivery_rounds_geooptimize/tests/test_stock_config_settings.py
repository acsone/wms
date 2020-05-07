# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestStockConfigSettings(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestStockConfigSettings, cls).setUpClass()
        cls.StockConfigSettings = cls.env["stock.config.settings"]
        cls.IrConfigParameter = cls.env["ir.config_parameter"]

    def test_00(self):
        """
        Data:
            nihil
        Test case:
            Update and load config
        Expected result:
            Values retrieved are those saved
        """
        self.StockConfigSettings.create(
            {
                "geo_optimization_enabled": True,
                "geo_optimization_api_url": "my_url",
                "geo_optimization_api_key": "api key",
                "geo_optimization_duration": 1,
                "geo_optimization_delivery_duration": 10,
                "geo_optimization_loading_duration": 100,
                "geo_optimization_resources_number": 5,
            }
        ).execute()
        config = self.StockConfigSettings.get_optimization_config()
        self.assertEqual(config.enabled, True)
        self.assertEqual(config.api_url, "my_url")
        self.assertEqual(config.api_key, "api key")
        self.assertEqual(config.duration, 1)
        self.assertEqual(config.delivery_duration, 10)
        self.assertEqual(config.loading_duration, 100)
        self.assertEqual(config.resources_number, 5)

        # an update on the parameters invalidate the config cache
        self.IrConfigParameter.set_param(
            "alc_delivery_rounds_geooptimize.geo_optimization_api_url", "new_url"
        )
        config = self.StockConfigSettings.get_optimization_config()
        self.assertEqual(config.api_url, "new_url")
