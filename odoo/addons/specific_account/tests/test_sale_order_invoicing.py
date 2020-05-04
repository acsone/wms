# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, tools
from odoo.tests.common import SavepointCase


class TestSaleOrderInvoicing(SavepointCase):
    at_install = False
    post_install = True

    @classmethod
    def setUpClass(cls):
        super(TestSaleOrderInvoicing, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.AccountInvoice = cls.env["account.invoice"]
        cls.StockReturnPicking = cls.env["stock.return.picking"]
        cls.SaleOrder = cls.env["sale.order"]

        cls.partner = cls.env["res.partner"].create(
            {"name": u"TEST", "customer": True, "ref": "42"}
        )
        cls.product = cls.env["product.product"].create(
            {"name": u"TEST", "type": "consu", "invoice_policy": "delivery"}
        )
        cls.orders = cls.env["sale.order"]
        cls.unique_orders = cls.env["sale.order"]
        cls.mergeable_orders = cls.env["sale.order"]
        # Generate 2 SO to invoice together
        # + 2 others SO to invoice separately
        for x in range(4):
            is_unique_invoice = bool(x % 2)
            order = cls.SaleOrder.create(
                {
                    "partner_id": cls.partner.id,
                    "partner_invoice_id": cls.partner.id,
                    "partner_shipping_id": cls.partner.id,
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

    def _process_picking(self, picking):
        picking.force_assign()
        picking.assign_operator()
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
        # 1 invoice for 2 SO + 2 invoices for SO invoiced separately => 3
        self.assertEqual(len(invoice_ids), 3)

    def test_00(self):
        """
        Data:
            1 SO delivered and invoiced SO (is_unique_invoice)
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
        # data
        delivered_and_invoiced_so = self.unique_orders[0]
        second_so = self.unique_orders[1]
        self._deliver_orders(delivered_and_invoiced_so)
        with tools.mute_logger("odoo.addons.queue_job.models.base"):
            self.SaleOrder.with_context(
                test_queue_job_no_delay=True
            )._job_invoices_by_partner(self.partner.id, fields.Datetime.now())

        # test case
        # return the delivered_and_invoiced_so
        self._return_orders(delivered_and_invoiced_so)
        # deliver a new so
        self._deliver_orders(second_so)
        invoices = self.AccountInvoice.search([])
        # create invoices
        with tools.mute_logger("odoo.addons.queue_job.models.base"):
            self.SaleOrder.with_context(
                test_queue_job_no_delay=True
            )._job_invoices_by_partner(self.partner.id, fields.Datetime.now())

        # expected result
        new_invoices = self.AccountInvoice.search([]) - invoices
        self.assertEqual(len(new_invoices), 2)
