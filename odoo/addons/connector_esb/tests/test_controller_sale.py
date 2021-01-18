# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from copy import deepcopy

from werkzeug.exceptions import BadRequest

from odoo.tests.common import SavepointCase

from odoo.addons.connector_esb.controllers.sale import SaleController


class ControllerSaleTestCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(ControllerSaleTestCase, cls).setUpClass()
        cls.controller = SaleController()
        cls.order_data = {
            "increment_id": "048300",
            "customer_id": "39847598274",
            "date": "2017-09-18",
            "order_ref": "refClt",
            "lines": [
                {"line_id": "1", "sku": "0001", "quantity": 3, "free": False},
                {
                    # free line: to be skipped
                    "line_id": "2",
                    "sku": "FOO",
                    "quantity": 3,
                    "free": True,
                },
            ],
        }
        cls.request_data = {
            "jsonrpc": "3.0",
            "id": "4321",
            "method": "create",
            "params": {"data": cls.order_data},
        }

    def test_valid_request_data(self):
        """ Check a valid request payload. """
        self.controller._validate_request(self.request_data)
        self.controller._validate_create_sale_order(self.order_data)

    def test_request_data(self):
        """ Check no params"""
        data = deepcopy(self.request_data)
        data.pop("params")
        with self.assertRaises(BadRequest):
            self.controller._validate_request(data)

    def test_required_invrement_id(self):
        data = deepcopy(self.order_data)
        data.pop("increment_id")
        with self.assertRaises(BadRequest):
            self.controller._validate_create_sale_order(data)

    def test_required_customer_id(self):
        data = deepcopy(self.order_data)
        data.pop("customer_id")
        with self.assertRaises(BadRequest):
            self.controller._validate_create_sale_order(data)

    def test_required_sale_date(self):
        data = deepcopy(self.order_data)
        data.pop("date")
        with self.assertRaises(BadRequest):
            self.controller._validate_create_sale_order(data)

    def test_required_order_lines(self):
        data = deepcopy(self.order_data)
        data.pop("lines")
        with self.assertRaises(BadRequest):
            self.controller._validate_create_sale_order(data)

    def test_valid_order_lines(self):
        """Check lines is a list"""
        data = deepcopy(self.order_data)
        data["lines"] = data["lines"][0]
        with self.assertRaises(BadRequest):
            self.controller._validate_create_sale_order(data)

    def test_sale_date_validity(self):
        data = deepcopy(self.order_data)
        data["date"] = "2019-02-18 12:12:12"
        self.controller._validate_create_sale_order(data)
        data["date"] = "2019-02-18"
        self.controller._validate_create_sale_order(data)

        data["date"] = "2019-02-18 asdf"
        with self.assertRaises(BadRequest):
            self.controller._validate_create_sale_order(data)
        data["date"] = "2019"
        with self.assertRaises(BadRequest):
            self.controller._validate_create_sale_order(data)
