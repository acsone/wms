# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo import fields
from odoo.tests.common import SavepointCase


class TestSaleOrderInvoicing(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestSaleOrderInvoicing, cls).setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context, tracking_disable=True, test_queue_job_no_delay=True
            )
        )
        cls.warehouse_1 = cls.env.ref("stock.warehouse0")
        cls.warehouse_1.out_type_id.create_invoice_on_transfer = True

        cls.AccountInvoice = cls.env["account.invoice"]
        cls.StockReturnPicking = cls.env["stock.return.picking"]
        cls.SaleOrder = cls.env["sale.order"]

        # force no payment mode on the partner to be able to create so without payment mode
        cls.partner = cls.env["res.partner"].create(
            {
                "name": u"TEST",
                "customer": True,
                "ref": "42",
                "customer_payment_mode_id": False,
            }
        )
        cls.product = cls.env["product.product"].create(
            {"name": u"TEST", "type": "consu", "invoice_policy": "delivery"}
        )
        cls.orders = cls.env["sale.order"]
        cls.unique_orders = cls.env["sale.order"]
        cls.mergeable_orders = cls.env["sale.order"]

        # payment mode
        cls.AccountPaymentMode = cls.env["account.payment.mode"]
        cls.journal_bank = cls.env["res.partner.bank"].create(
            {
                "acc_number": "GB95LOYD87430237296288",
                "partner_id": cls.env.user.company_id.id,
            }
        )
        cls.journal = cls.env["account.journal"].create(
            {
                "name": "BANK TEST",
                "code": "TEST",
                "type": "bank",
                "bank_account_id": cls.journal_bank.id,
            }
        )
        cls.payment_mode = cls.env["account.payment.mode"].create(
            {
                "name": "Payment Mode Inbound",
                "payment_method_id": cls.env.ref(
                    "account.account_payment_method_manual_in"
                ).id,
                "bank_account_link": "fixed",
                "fixed_journal_id": cls.journal.id,
            }
        )

        # Generate 8 SO
        # * 2 SO to invoice together without payment_mode
        # * 2 SO to invoice together with payment_mode
        # * 2 SO to invoice separately without payment_mode
        # * 2 SO to invoice separately with payment_mode
        payment_mode_id = False
        for x in range(8):
            is_unique_invoice = bool(x % 2)
            payment_mode_id = cls.payment_mode.id if x in [0, 1, 4, 5] else False
            order = cls.SaleOrder.create(
                {
                    "partner_id": cls.partner.id,
                    "partner_invoice_id": cls.partner.id,
                    "partner_shipping_id": cls.partner.id,
                    "payment_mode_id": payment_mode_id,
                    "order_line": [
                        (
                            0,
                            0,
                            {
                                "name": u"Line {}".format(i),
                                "product_id": cls.product.id,
                                "product_uom_qty": 4,
                                "product_uom": cls.product.uom_id.id,
                                "price_unit": i,
                            },
                        )
                        for i in range(4)
                    ],
                    "pricelist_id": cls.env.ref("product.list0").id,
                    "is_unique_invoice": is_unique_invoice,
                }
            )
            cls.orders |= order
            if is_unique_invoice:
                cls.unique_orders |= order
            else:
                cls.mergeable_orders |= order

        # cancel invoiceable so
        invoiceable_orders = cls.SaleOrder.search(
            [("invoice_status", "=", "to invoice")]
        )
        invoiceable_orders.action_cancel()

    def setUp(self):
        super(TestSaleOrderInvoicing, self).setUp()
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

    def _process_picking(self, picking):
        picking.force_assign()
        for pack in picking.pack_operation_product_ids:
            pack.qty_done = pack.product_qty
        picking.do_new_transfer()

    def _deliver_orders(self, orders):
        for order in orders:
            # validate SO
            order.action_confirm()
            # process deliveries
            picking_internals = order.picking_ids.filtered(
                lambda p: p.picking_type_code == "internal"
            )
            picking_outs = order.picking_ids.filtered(
                lambda p: p.picking_type_code == "outgoing"
            )
            for picking in picking_internals:
                self._process_picking(picking)
                self.assertEqual(picking.state, "done")
            for picking in picking_outs:
                self._process_picking(picking)
                self.assertEqual(picking.state, "done")

    def _return_orders(self, orders):
        for pick in orders.mapped("picking_ids"):
            # Create return picking
            default_data = self.StockReturnPicking.with_context(
                active_ids=pick.ids, active_id=pick.ids[0]
            ).default_get(
                [
                    "move_dest_exists",
                    "original_location_id",
                    "product_return_moves",
                    "parent_location_id",
                    "location_id",
                ]
            )
            return_wiz = self.StockReturnPicking.with_context(
                active_ids=pick.ids, active_id=pick.ids[0]
            ).create(default_data)
            return_wiz.product_return_moves.write(
                {"quantity": 4.0, "to_refund_so": True}  # Return all products
            )
            res = return_wiz.create_returns()
            return_pick = (
                self.env["stock.picking"]
                .browse(res["res_id"])
                .with_context(__no_pick_receive_note_check=True)
            )

            # Validate picking
            return_pick.force_assign()
            return_pick.pack_operation_product_ids.write({"qty_done": 16})
            return_pick.do_new_transfer()

    def test_is_unique_invoice(self):
        self._deliver_orders(self.orders)
        invoice_ids = self.orders.action_invoice_create(final=True)
        # 1 invoice for 4 SO + 4 invoices for SO invoiced separately => 5
        self.assertEqual(len(invoice_ids), 5)

    def test_00(self):
        """
        Data:
            1 SO delivered and invoiced SO (is_unique_invoice) with the same
            payment mode
        Test case:
            Return delivered SO
            Deliver a new is_unique_invoice SO for the same partner with
            invoice policy 'all_at_once'
            Create invoice for this partner
            (At this stage we have 2 SO to invoices separately;
            the new one and the refund of the one returned)
        Expected result:
            2 invoices must be created. 1 invoice and 1 refund
        """
        unique_orders = self.unique_orders.filtered(lambda a: not a.payment_mode_id)
        delivered_and_invoiced_so = unique_orders[0]
        second_so = unique_orders[1]
        self._deliver_orders(delivered_and_invoiced_so)
        self.SaleOrder._job_invoices_by_partner(
            self.partner.id,
            delivered_and_invoiced_so.payment_mode_id.id,
            fields.Datetime.now(),
        )

        # test case
        # return the delivered_and_invoiced_so
        self._return_orders(delivered_and_invoiced_so)
        # deliver a new so
        self._deliver_orders(second_so)
        invoices = self.AccountInvoice.search([])
        # create invoices
        self.SaleOrder._job_invoices_by_partner(
            self.partner.id,
            delivered_and_invoiced_so.payment_mode_id.id,
            fields.Datetime.now(),
        )

        # expected result
        new_invoices = self.AccountInvoice.search([]) - invoices
        self.assertEqual(2, len(new_invoices))

    def test_01(self):
        """
        Data:
            * 2 SO to invoice together without payment_mode
            * 2 SO to invoice together with payment_mode
            * payment_mode:
                invoice_frequency: False
                invoice_grouping: False
            * partner:
                invoice_frequency: 10_days
                invoice_grouping: all_at_once
        Test Case
            run scheduller for a normal day
        Expected Result:
            2 invoices must be created:
                1 invoice without paument_mode
                1 invoice with payment_mode
        """
        self.partner.write(
            {"invoice_frequency": "10_days", "invoice_grouping": "all_at_once"}
        )
        self._deliver_orders(self.mergeable_orders)
        invoices = self.AccountInvoice.search([])
        self.SaleOrder._cron_invoice_makeall(10)
        new_invoices = self.AccountInvoice.search([]) - invoices
        self.assertEqual(2, len(new_invoices))

    def test_02(self):
        """
        Data:
            * picking type configured with create_invoice_on_transfer=True
            * 2 SO to invoice together without payment_mode
            * 2 SO to invoice together with payment_mode
            * payment_mode:
                invoice_frequency: 10_days
                invoice_grouping: by_delivery
            * partner:
                invoice_frequency: 10_days
                invoice_grouping: all_at_once
        Test Case
            1. deliver orders
            2. run scheduler for a normal day
        Expected Result:
            1. 2 invoices must be created in draft mode for the 2 so with payment_mode
            2. 1 more invoice is created and open for the 2 so without payment mode
               the 2 first invoices are now open
        """
        self.partner.write(
            {"invoice_frequency": "10_days", "invoice_grouping": "all_at_once"}
        )
        self.payment_mode.write(
            {"invoice_frequency": "10_days", "invoice_grouping": "by_delivery"}
        )
        invoices = self.AccountInvoice.search([])
        self._deliver_orders(self.mergeable_orders)
        draft_invoices = self.AccountInvoice.search([]) - invoices
        invoices = self.AccountInvoice.search([])
        self.assertEqual(2, len(draft_invoices))
        self.assertSetEqual(
            set(self.mergeable_orders.filtered("payment_mode_id").mapped("name")),
            set(draft_invoices.mapped("origin")),
        )
        self.assertEqual(self.payment_mode, draft_invoices.mapped("payment_mode_id"))
        self.assertListEqual(["draft", "draft"], draft_invoices.mapped("state"))
        self.SaleOrder._cron_invoice_makeall(10)
        new_invoices = self.AccountInvoice.search([]) - invoices
        self.assertEqual(1, len(new_invoices))
        self.assertSetEqual(
            set(
                self.mergeable_orders.filtered(lambda a: not a.payment_mode_id).mapped(
                    "name"
                )
            ),
            set(new_invoices.origin.split(", ")),
        )
        self.assertFalse(new_invoices.mapped("payment_mode_id"))
        self.assertEqual("open", new_invoices.state)
        self.assertListEqual(["open", "open"], draft_invoices.mapped("state"))
