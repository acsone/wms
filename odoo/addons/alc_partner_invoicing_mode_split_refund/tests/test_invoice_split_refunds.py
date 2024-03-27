# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.tests import Form
from odoo.tests.common import TransactionCase

from odoo.addons.partner_invoicing_mode.tests.common import CommonPartnerInvoicingMode


class TestInvoiceSplitRefunds(CommonPartnerInvoicingMode, TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, queue_job__no_delay=True))
        cls.sale_order = cls.so1
        cls.product2 = cls.env.ref("product.product_delivery_02")
        cls.env["stock.quant"]._update_available_quantity(
            cls.product, cls.env.ref("stock.stock_location_stock"), 4
        )
        cls.sol1 = cls.sale_order.order_line
        cls.sol2 = cls.env["sale.order.line"].create(
            {
                "name": "Line two",
                "product_id": cls.product2.id,
                "product_uom_qty": 4,
                "product_uom": cls.product.uom_id.id,
                "price_unit": 100,
                "order_id": cls.sale_order.id,
            }
        )
        cls.sale_order.action_confirm()
        cls.picking = cls.sale_order.picking_ids

    @classmethod
    def _deliver(cls, sale_order):
        picking = sale_order.picking_ids.filtered(lambda p: p.state == "assigned")
        picking.action_set_quantities_to_reservation()
        picking._action_done()

    @classmethod
    def _create_backorder(cls, picking, quantity):
        stock_return_picking_form = Form(
            cls.env["stock.return.picking"].with_context(
                active_ids=picking.ids,
                active_id=picking.id,
                active_model="stock.picking",
            )
        )
        stock_return_picking = stock_return_picking_form.save()
        stock_return_picking.product_return_moves.write({"quantity": quantity})
        action = stock_return_picking.create_returns()
        return_pick = cls.env["stock.picking"].browse(action["res_id"])
        return_pick.move_ids.write({"quantity_done": quantity})
        return_pick._action_done()
        return return_pick

    def _create_and_deliver_order(self):
        sale_order_2 = self.sale_order.copy({})
        sale_order_2.action_confirm()
        self._deliver(sale_order_2)
        self.assertEqual(sale_order_2.order_line[0].qty_to_invoice, 2)
        return sale_order_2

    def _test_0(self):
        """
        1

        deliver first sale line
        2. run invoice cron
        3. deliver the second line and make partial return for the first
        """
        self._deliver(self.sale_order)
        self.assertEqual(self.sol1.qty_delivered, 4)
        self.assertEqual(self.sol1.qty_invoiced, 0)
        self.assertEqual(self.sol2.qty_delivered, 0)
        self.assertEqual(self.sol2.qty_invoiced, 0)
        self.env["sale.order"].cron_generate_standard_invoices()
        self.assertEqual(self.sol1.qty_invoiced, 4)
        self.env["stock.quant"]._update_available_quantity(
            self.product2, self.env.ref("stock.stock_location_stock"), 4
        )
        self.sol2.move_ids.picking_id.action_assign()
        self._deliver(self.sale_order)
        self.assertEqual(self.sol2.qty_delivered, 4)
        self.assertEqual(self.sol2.qty_to_invoice, 4)
        self._create_backorder(self.picking, 2)
        self.assertEqual(self.sol1.qty_delivered, 2)
        self.assertEqual(self.sol1.qty_to_invoice, -2)

    def _assert_invoice_and_refund_split(self):
        self.assertEqual(self.sol1.qty_invoiced, 2)
        self.assertEqual(self.sol2.qty_invoiced, 4)
        self.assertEqual(len(self.sale_order.invoice_ids), 3)
        self.assertSetEqual(
            set(self.sale_order.invoice_ids.mapped("move_type")),
            {"out_invoice", "out_refund"},
        )

    def test_0(self):
        """
        Make sure refund is split from invoice.

        --> 2 invoices and one refund expected
        """
        self._test_0()
        self.env["sale.order"].cron_generate_standard_invoices()
        self._assert_invoice_and_refund_split()

    def test_1(self):
        """
        Test group sale order by invoices is respected.

        one_invoice_per_order = False --> one invoice for both orders
        """
        self.sale_order.partner_id.one_invoice_per_order = False
        self.sale_order._compute_one_invoice_per_order()
        self._test_0()
        sale_order_2 = self._create_and_deliver_order()
        self.env["sale.order"].cron_generate_standard_invoices()
        self._assert_invoice_and_refund_split()
        self.assertEqual(len(sale_order_2.invoice_ids), 1)
        self.assertEqual(
            sale_order_2.invoice_ids.invoice_line_ids.sale_line_ids.order_id,
            self.sale_order | sale_order_2,
        )

    def test_2(self):
        """
        Test group sale order by invoices is respected.

        one_invoice_per_order = True --> an invoice for each order
        """
        self.sale_order.partner_id.one_invoice_per_order = True
        self.sale_order._compute_one_invoice_per_order()
        self._test_0()
        sale_order_2 = self._create_and_deliver_order()
        self.env["sale.order"].cron_generate_standard_invoices()
        self.assertEqual(len(sale_order_2.invoice_ids), 1)
        self.assertEqual(
            sale_order_2.invoice_ids.invoice_line_ids.sale_line_ids.order_id,
            sale_order_2,
        )
