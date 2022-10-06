# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from contextlib import contextmanager

import mock

from odoo.tests.common import SavepointCase
from odoo.tools import mute_logger

from odoo.addons.base_rest.controllers.main import _PseudoCollection
from odoo.addons.component.core import WorkContext
from odoo.addons.component.tests.common import ComponentMixin


class TestOrders(SavepointCase, ComponentMixin):
    @classmethod
    def _get_vals_sale_line(cls, product):
        return {
            "name": product.name,
            "product_id": product.id,
            "product_uom_qty": 1,
            "product_uom": product.uom_id.id,
            "price_unit": 10,
        }

    @classmethod
    def _get_vals_sale_order(cls, partner=None, products=None):
        products = products or cls.product
        return {
            "partner_id": (partner or cls.partner).id,
            "order_line": [(0, 0, cls._get_vals_sale_line(p)) for p in products],
        }

    @classmethod
    @mute_logger("odoo.addons.queue_job.models.base")
    def setUpClass(cls):
        super(TestOrders, cls).setUpClass()
        cls.setUpComponent()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        vals_partner = {"name": "P", "ref": "1214"}
        cls.partner = cls.env["res.partner"].create(vals_partner)
        vals_product = {"name": "Product", "default_code": "REF"}
        cls.product = cls.env["product.product"].create(vals_product)

        cls.so_model = cls.env["sale.order"]
        vals_sale_order = cls._get_vals_sale_order()
        cls.sale_order = cls.so_model.create(vals_sale_order)

    @classmethod
    @contextmanager
    def orders_service(cls, partner=None):
        partner_id = (partner or cls.partner).id
        context = dict(cls.env.context, authenticated_partner_id=partner_id)
        env = cls.env(context=context)
        collection = _PseudoCollection("shopinvader.backend", env)
        work = WorkContext(
            model_name="rest.service.registration",
            collection=collection,
            request=mock.Mock(),
            authenticated_partner_id=partner_id,
        )
        yield work.component(usage="orders")

    def setUp(self):
        super(TestOrders, self).setUp()
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
