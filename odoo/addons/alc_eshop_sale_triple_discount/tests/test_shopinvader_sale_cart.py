# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from contextlib import contextmanager

import mock

from odoo.tools import mute_logger

from odoo.addons.base_rest.controllers.main import _PseudoCollection
from odoo.addons.component.core import WorkContext
from odoo.addons.shopinvader.tests.common import CommonCase


class TestShopinvaderSaleCart(CommonCase):
    @classmethod
    @mute_logger("odoo.addons.queue_job.models.base")
    def setUpClass(cls):
        super(TestShopinvaderSaleCart, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, test_queue_job_no_delay=True))
        cls.product_1 = cls.env.ref("product.product_product_4b")
        cls.partner = cls.env.ref("shopinvader.partner_1")
        cls.so = cls._create_cart()
        cls.so.order_line.discount2 = 10
        cls.so.order_line.discount3 = 10

    def setUp(self):
        super(TestShopinvaderSaleCart, self).setUp()
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

    @classmethod
    @contextmanager
    def cart_service(cls, authenticated_partner_id=None):
        authenticated_partner_id = authenticated_partner_id or cls.partner.id
        env = cls.env(
            context=dict(
                cls.env.context, authenticated_partner_id=authenticated_partner_id,
            )
        )
        collection = _PseudoCollection("shopinvader.api.v2", env)
        work = WorkContext(
            model_name="rest.service.registration",
            collection=collection,
            request=mock.Mock(),
            authenticated_partner_id=authenticated_partner_id,
            shopinvader_backend=cls.backend,
        )
        yield work.component(usage="cart")

    @classmethod
    @contextmanager
    def sales_service(cls, authenticated_partner_id=None):
        authenticated_partner_id = authenticated_partner_id or cls.partner.id
        env = cls.env(
            context=dict(
                cls.env.context, authenticated_partner_id=authenticated_partner_id,
            )
        )
        collection = _PseudoCollection("shopinvader.backend", env)
        work = WorkContext(
            model_name="rest.service.registration",
            collection=collection,
            request=mock.Mock(),
            authenticated_partner_id=authenticated_partner_id,
            partner=cls.env["res.partner"].browse(authenticated_partner_id),
            shopinvader_backend=cls.backend,
        )
        yield work.component(usage="sales")

    @classmethod
    def _create_cart(cls, authenticated_partner_id=None):
        with cls.cart_service(
            authenticated_partner_id=authenticated_partner_id
        ) as cart:
            info = cart._create_empty_cart()
            info = cart.sync(
                uuid=info["uuid"],
                transactions=[
                    {"uuid": "uuid1", "product_id": cls.product_1.id, "qty": 1}
                ],
            )
            return cls.env["sale.order"].browse(info["id"])

    def test_cart_price_and_discount_info(self):
        with self.cart_service() as cart:
            info = cart.sync(uuid=self.so.uuid, transactions=[])
            self.assertTrue(info)
            line = info["lines"][0]
            self.assertEqual(line["unit_price"]["untaxed_with_discount"], 607.5)
            self.assertEqual(line["discount"]["rate"], 19)

    def test_sale_price_and_discount_info(self):
        self.so.action_confirm()
        with self.sales_service() as sales:
            info = sales.get(self.so.id)
            self.assertTrue(info)
            line = info["lines"]["items"][0]
            self.assertEqual(line["unit_price"]["untaxed_with_discount"], 607.5)
            self.assertEqual(line["discount"]["rate"], 19)

    def test_priclist_discount_multiple_min_qty(self):
        discount_pricelist_5 = self.env["product.pricelist"].create(
            {
                "name": "Unittest Discount Pricelist 5",
                "item_ids": [
                    (
                        0,
                        False,
                        {
                            "applied_on": "1_product",
                            "product_id": self.product_1.id,
                            "compute_price": "percentage",
                            "percent_price": 5,
                        },
                    )
                ],
            }
        )
        discount_pricelist_10 = self.env["product.pricelist"].create(
            {
                "name": "Unittest Discount Pricelist 10",
                "item_ids": [
                    (
                        0,
                        False,
                        {
                            "applied_on": "1_product",
                            "product_id": self.product_1.id,
                            "compute_price": "percentage",
                            "percent_price": 10,
                            "min_quantity": 10,
                        },
                    )
                ],
            }
        )
        discount_item_5 = discount_pricelist_5.item_ids
        discount_item_10 = discount_pricelist_10.item_ids
        line = self.so.order_line
        self.assertFalse(line.discount_item_id)
        self.so.discount_pricelist_ids = discount_pricelist_5 | discount_pricelist_10
        with self.cart_service() as cart:
            info = cart.sync(
                uuid=self.so.uuid,
                transactions=[
                    {"uuid": "uuid1", "product_id": self.product_1.id, "qty": 5}
                ],
            )
            self.assertTrue(info)

        line = self.so.order_line
        line.refresh()
        self.assertEqual(discount_item_5, line.discount_item_id)
        self.assertEqual(5, line.discount3)

        with self.cart_service() as cart:
            info = cart.sync(
                uuid=self.so.uuid,
                transactions=[
                    {"uuid": "uuid1", "product_id": self.product_1.id, "qty": 5}
                ],
            )
            self.assertTrue(info)
        self.assertEqual(discount_item_10, line.discount_item_id)
        self.assertEqual(10, line.discount3)

        with self.cart_service() as cart:
            info = cart.sync(
                uuid=self.so.uuid,
                transactions=[
                    {"uuid": "uuid1", "product_id": self.product_1.id, "qty": -5}
                ],
            )
            self.assertTrue(info)
        self.assertEqual(discount_item_5, line.discount_item_id)
        self.assertEqual(5, line.discount3)
