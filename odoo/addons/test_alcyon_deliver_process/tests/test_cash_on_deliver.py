# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import Command

from odoo.addons.queue_job.tests.common import trap_jobs

from .common import TestDeliverProcessBase


class TestCashOndeliver(TestDeliverProcessBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, queue_job__no_delay=False))
        cls.channel = cls.channel.with_context(queue_job__no_delay=False)
        cls.product = cls.env["product.product"].create(
            {"name": "Test product", "tracking": "none", "type": "product"}
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.product, cls.loc_stock, 100.0
        )
        cls.pay_terms_cash_on_delivery = cls.env["account.payment.term"].create(
            {
                "name": "Cash on delivery",
                "cash_on_delivery": True,
                "line_ids": [Command.create({"value": "balance", "value_amount": 0})],
            }
        )

    def test_0(self):
        self.warehouse_1.route_ids.rule_ids.propagate_carrier = True
        with trap_jobs() as trap:
            sale = self._confirm_sale_order(products=[self.product], qty=2)
            trap.perform_enqueued_jobs()
        sale.payment_term_id = self.pay_terms_cash_on_delivery
        with trap_jobs() as trap:
            self.channel.action_unlock()
            trap.perform_enqueued_jobs()

        ship = self._get_picking_ship(sale)
        pick = self._get_picking_pick(sale)
        self.assertEqual(len(ship), 1)
        self.assertEqual(len(pick), 1)
        self.assertEqual(pick.release_channel_id, self.channel)
        pick.move_line_ids.qty_done = 2
        pick._action_done()
        self.channel.action_lock()
        with trap_jobs() as trap_rc:
            self.channel.action_deliver()
            self.assertEqual(self.channel.state, "delivering")
            with trap_jobs() as trap_sa:
                trap_rc.perform_enqueued_jobs()
                self.channel.shipment_advice_ids.filtered(
                    lambda s: s.state not in ("done", "cancel")
                )
                with trap_jobs() as trap_sap:
                    # picking jobs
                    trap_sa.perform_enqueued_jobs()
                    trap_sap.perform_enqueued_jobs()
        self.assertFalse(self.channel.delivering_error)
        self.assertEqual(self.channel.state, "delivered")
        self.assertTrue(ship.cash_on_delivery_invoice_ids)
        self.assertEqual(ship.cash_on_delivery_invoice_ids.state, "posted")
        action = self.channel.with_context(
            discard_logo_check=True
        ).action_print_cash_invoices()
        self.assertEqual(
            action.get("context").get("active_ids"),
            ship.cash_on_delivery_invoice_ids.ids,
        )
