# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from unittest import mock

from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger


class TestAlcSaleCartPriceRecalculation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                tracking_disable=True,
                queue_job__no_delay=True,
            )
        )
        cls.partner = cls.env.ref("base.res_partner_1")
        cls.partner.ref = "123321"
        cls.sale = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "date_order": "2019-10-10",
                "client_order_ref": "whatever the client want",
                "order_line": [],
            }
        )

    @mute_logger("odoo.addons.queue_job.utils")
    def test_cart_recompute_triggered(self):
        """Check that the cart recompute job is triggered."""
        self.sale.write({"date_order": "2017-01-01 00:00:00", "typology": "cart"})
        # recalculate only apply to past cart
        with mock.patch.object(
            self.sale.__class__, "action_update_prices"
        ) as mock_recalculate_prices:
            self.sale._cron_recompute_cart_price()
            self.assertTrue(mock_recalculate_prices.called)
        # once updated a new call to the cron is without effect
        with mock.patch.object(
            self.sale.__class__, "action_update_prices"
        ) as mock_recalculate_prices:
            self.sale._cron_recompute_cart_price()
            self.assertFalse(mock_recalculate_prices.called)

        # check that the cart is not updated if it is not a cart
        self.sale.write({"date_order": "2017-01-01 00:00:00", "typology": "sale"})
        with mock.patch.object(
            self.sale.__class__, "action_update_prices"
        ) as mock_recalculate_prices:
            self.sale._cron_recompute_cart_price()
            self.assertFalse(mock_recalculate_prices.called)
