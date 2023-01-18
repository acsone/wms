# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import mock

from odoo.addons.alc_pricelist_discount.tests.common import PricelistDiscountCase


class TestAlcSaleCartPriceRecalculation(PricelistDiscountCase):
    @classmethod
    def setUpClass(cls):
        super(TestAlcSaleCartPriceRecalculation, cls).setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context, tracking_disable=True, test_queue_job_no_delay=True,
            )
        )
        cls.sale = cls.sale.with_context(**cls.env.context)

    def test_cart_recompute_triggered(self):
        """
        Check that the cart recompute job is triggered
        """
        self.sale.write(dict(date_order="2017-01-01 00:00:00", typology="cart"))
        # recalculate only apply to past cart
        with mock.patch.object(
            self.sale.__class__, "recalculate_prices"
        ) as mock_recalculate_prices:
            self.sale._cron_recompute_cart_price()
            self.assertTrue(mock_recalculate_prices.called)
        # once updated a new call to the cron is without effect
        with mock.patch.object(
            self.sale.__class__, "recalculate_prices"
        ) as mock_recalculate_prices:
            self.sale._cron_recompute_cart_price()
            self.assertFalse(mock_recalculate_prices.called)

        # check that the cart is not updated if it is not a cart
        self.sale.write(dict(date_order="2017-01-01 00:00:00", typology="sale"))
        with mock.patch.object(
            self.sale.__class__, "recalculate_prices"
        ) as mock_recalculate_prices:
            self.sale._cron_recompute_cart_price()
            self.assertFalse(mock_recalculate_prices.called)
