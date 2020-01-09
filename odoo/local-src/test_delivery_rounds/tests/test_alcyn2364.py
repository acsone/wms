# coding: utf-8

from .common import TestDeliveryRound


class DeliveryFees(TestDeliveryRound):
    """Tests for ALCYN-2364. Check shipping fees invoice"""

    @classmethod
    def setUpClass(cls):
        super(DeliveryFees, cls).setUpClass()
        # set the partners
        cls.partner1.help_with_fee = True
        cls.partner1.invoice_frequency = '10_days'
        cls.partner1.invoice_grouping = 'by_delivery'

        cls.partner2.help_with_fee = True
        cls.partner2.invoice_frequency = '10_days'
        cls.partner2.invoice_grouping = 'by_delivery'

        # round is in draft and open
        cls.delivery_round_1.button_resetdraft()

    def test_invoicing_shipping_fees_1_sale_order(self):
        """ We whant to be sure the shipping fees are invoiced.
        """
        # create sale order
        so1 = self._confirm_sale_order(self.partner1, product=self.p1, qty=10)
        # add carrier to so
        so1.carrier_id = self.delivery_method
        # assign picking to the delivery round
        self.delivery_round_1._assign_pickings(so1.picking_ids)
        self.delivery_round_1.button_picking_start()
        preparation = so1.picking_ids.filtered(
            lambda p: p.picking_type_id == self.warehouse_1.pick_type_id
        )
        pack_op = preparation.pack_operation_ids[0]
        pack_op.qty_done = 10.0
        preparation.do_new_transfer()
        # close round
        self.delivery_round_1.button_close()
        self.delivery_round_1.with_context(
            test_queue_job_no_delay=True
        )._deliver(background=False)
        self.delivery_round_1.button_done()
        so_invoice_status = so1.mapped('order_line.invoice_status')
        self.assertEqual(so_invoice_status, ['invoiced', 'invoiced'])

    def test_invoicing_shipping_fees_2_sale_order(self):
        """ The shipping fees are invoiced and only on the last sale order.
        """
        # create sale orders
        so1 = self._confirm_sale_order(self.partner1, product=self.p1, qty=10)
        so2 = self._confirm_sale_order(self.partner1, product=self.p2, qty=5)

        for so in [so1, so2]:
            # add carrier to so
            so.carrier_id = self.delivery_method
            # assign picking to the delivery round
            self.delivery_round_1._assign_pickings(so.picking_ids)

        self.delivery_round_1.button_picking_start()
        preparation = so1.picking_ids.filtered(
            lambda p: p.picking_type_id == self.warehouse_1.pick_type_id
        )
        preparation += so2.picking_ids.filtered(
            lambda p: p.picking_type_id == self.warehouse_1.pick_type_id
        )
        pack_op = preparation.mapped('pack_operation_ids')
        pack_op[0].qty_done = 10.0
        pack_op[1].qty_done = 5.0
        for prep in preparation:
            prep.do_new_transfer()
        # close round
        self.delivery_round_1.button_close()
        self.delivery_round_1.with_context(
            test_queue_job_no_delay=True
        )._deliver(background=False)
        self.delivery_round_1.button_done()
        so1_invoice_status = so1.mapped('order_line.invoice_status')
        so2_invoice_status = so2.mapped('order_line.invoice_status')
        self.assertEqual(so1_invoice_status, ['invoiced'])
        # the fees should be invoiced only on the last sale order
        self.assertEqual(so2_invoice_status, ['invoiced', 'invoiced'])

    def test_invoicing_shipping_fees_2_sale_order_from_2_partners(self):
        """ Only the first customer SO will be prepared.

        The 2nd should no invoiceble.
        """
        # create sale orders
        so1 = self._confirm_sale_order(self.partner1, product=self.p1, qty=10)
        so2 = self._confirm_sale_order(self.partner2, product=self.p2, qty=5)

        for so in [so1, so2]:
            # add carrier to so
            so.carrier_id = self.delivery_method
            # assign picking to the delivery round
            self.delivery_round_1._assign_pickings(so.picking_ids)

        self.delivery_round_1.button_picking_start()
        # prepare only the so1
        preparation = so1.picking_ids.filtered(
            lambda p: p.picking_type_id == self.warehouse_1.pick_type_id
        )
        pack_op = preparation.mapped('pack_operation_ids')
        pack_op[0].qty_done = 10.0
        preparation.do_new_transfer()
        # close round
        self.delivery_round_1.button_close()
        self.delivery_round_1.with_context(
            test_queue_job_no_delay=True
        )._deliver(background=False)
        self.delivery_round_1.button_done()
        so1_invoice_status = so1.mapped('order_line.invoice_status')
        so2_invoice_status = so2.mapped('order_line.invoice_status')
        self.assertEqual(so1_invoice_status, ['invoiced', 'invoiced'])
        self.assertEqual(so2_invoice_status, ['to invoice'])
