# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo.tests.common import SavepointCase


class TestSaleOrderInvoicing(SavepointCase):
    at_install = False
    post_install = True

    @classmethod
    def setUpClass(cls):
        super(TestSaleOrderInvoicing, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner = cls.env['res.partner'].create(
            {'name': u"TEST", 'is_customer': True}
        )
        cls.product = cls.env['product.product'].create(
            {'name': u"TEST", 'type': 'consu'}
        )
        cls.orders = cls.env['sale.order']
        # Generate 2 SO to invoice together
        # + 2 others SO to invoice separately
        for x in range(4):
            is_unique_invoice = bool(x % 2)
            order = cls.env['sale.order'].create(
                {
                    'partner_id': cls.partner.id,
                    'partner_invoice_id': cls.partner.id,
                    'partner_shipping_id': cls.partner.id,
                    'order_line': [
                        (
                            0,
                            0,
                            {
                                'name': u"Line {}".format(i),
                                'product_id': cls.product.id,
                                'product_uom_qty': 1,
                                'product_uom': cls.product.uom_id.id,
                                'price_unit': i,
                            },
                        )
                        for i in range(4)
                    ],
                    'pricelist_id': cls.env.ref('product.list0').id,
                    'is_unique_invoice': is_unique_invoice,
                }
            )
            cls.orders |= order

    def _process_picking(self, picking):
        picking.force_assign()
        picking.assign_operator()
        for pack in picking.pack_operation_product_ids:
            pack.qty_done = pack.product_qty
        picking.do_new_transfer()

    def test_is_unique_invoice(self):
        for order in self.orders:
            # validate SO
            order.action_confirm()
            # process deliveries
            picking_internals = order.picking_ids.filtered(
                lambda p: p.picking_type_code == 'internal'
            )
            picking_outs = order.picking_ids.filtered(
                lambda p: p.picking_type_code == 'outgoing'
            )
            for picking in picking_internals:
                self._process_picking(picking)
                self.assertEqual(picking.state, 'done')
            for picking in picking_outs:
                self._process_picking(picking)
                self.assertEqual(picking.state, 'done')
        invoice_ids = self.orders.action_invoice_create(final=True)
        # 1 invoice for 2 SO + 2 invoices for SO invoiced separately => 3
        self.assertEqual(len(invoice_ids), 3)
