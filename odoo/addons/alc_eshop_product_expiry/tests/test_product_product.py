# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from datetime import datetime, timedelta

from odoo import fields

from odoo.addons.connector_search_engine.tests.models import SeAdapterFake
from odoo.addons.shopinvader_product_stock.tests.common import StockCommonCase


class TestProductProduct(StockCommonCase):
    @classmethod
    def setUpClass(cls):
        super(TestProductProduct, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, test_queue_job_no_delay=True))
        cls.production_lot_model = cls.env["stock.production.lot"]
        cls.inventory_model = cls.env["stock.inventory"]
        cls.inventory_line_model = cls.env["stock.inventory.line"]
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.loc_physical = cls.env.ref("alc_stock_location_data.stock_location_vlb")
        cls.stock_location.location_id = cls.loc_physical
        cls.env["stock.location"].search([])._parent_store_compute()
        # avoid trouble with gitlab since odoo storage is not preserved with
        # the cached db when running tests
        for xml_id in [
            "shopinvader_image.ir_exp_shopinvader_variant_images",
            "shopinvader_image.ir_exp_shopinvader_category_images",
        ]:
            ir_export = cls.env.ref(xml_id, raise_if_not_found=False)
            if ir_export:
                ir_export.unlink()

    def setUp(self):
        super(TestProductProduct, self).setUp()
        self.product.tracking = "lot"
        self.shop_product = self.product.shopinvader_bind_ids
        self.shop_product.data = {self.shop_product._get_stock_export_key(): {}}
        self.shop_product.sync_state = "done"
        self.production_lot = self.production_lot_model.create(
            {"name": "000001", "product_id": self.product.id}
        )
        # mute logger
        loggers = ["odoo.addons.queue_job.models.base"]
        for logger in loggers:
            logging.getLogger(logger).addFilter(self)

        # pylint: disable=unused-variable
        @self.addCleanup
        def un_mute_logger():
            for logger_ in loggers:
                logging.getLogger(logger_).removeFilter(self)

    def filter(self, record):
        # required to mute logger
        return 0

    def _add_product_qty(self, product, production_lot, quantity):
        self.inventory = self.inventory_model.create(
            {
                "name": "Unittest Inventory",
                "location_id": self.stock_location.id,
                "filter": "partial",
            }
        )
        self.inventory.prepare_inventory()

        self.inventory_line_model.create(
            {
                "inventory_id": self.inventory.id,
                "product_id": product.id,
                "location_id": self.stock_location.id,
                "product_qty": quantity,
                "prod_lot_id": production_lot.id,
            }
        )
        self.inventory.action_done()

    def test_best_order_date_on_lot_input(self):
        self.production_lot.life_date = fields.Datetime.to_string(
            datetime.now() + timedelta(weeks=2)
        )
        self.assertFalse(self.shop_product.data.get("best_before_date"), "")
        with SeAdapterFake.mocked_calls():
            self._add_product_qty(
                self.product, production_lot=self.production_lot, quantity=10
            )
        self.assertEqual(
            self.shop_product.data.get("best_before_date"),
            self.production_lot.life_date[:10],
        )

        # add a lot with an older date...
        new_lot = self.production_lot.copy(
            {
                "name": "lot2",
                "life_date": fields.Datetime.to_string(
                    datetime.now() + timedelta(weeks=1)
                ),
            }
        )
        with SeAdapterFake.mocked_calls():
            self._add_product_qty(self.product, production_lot=new_lot, quantity=10)
        self.assertEqual(
            self.shop_product.data.get("best_before_date"), new_lot.life_date[:10]
        )

    def test_best_before_date_in_data(self):
        self.production_lot.life_date = fields.Datetime.to_string(
            datetime.now() + timedelta(weeks=2)
        )
        with SeAdapterFake.mocked_calls():
            self._add_product_qty(
                self.product, production_lot=self.production_lot, quantity=10
            )
        self.shop_product.recompute_json()
        self.assertIn("best_before_date", self.shop_product.data)
        self.assertEqual(
            self.production_lot.life_date[:10],
            self.shop_product.data["best_before_date"],
        )
