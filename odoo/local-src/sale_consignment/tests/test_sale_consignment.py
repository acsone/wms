# -*- coding: utf-8 -*-
# Copyright 2020 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import SavepointCase


class TestSaleconsignment(SavepointCase):
    at_install = False
    post_install = True

    @classmethod
    def setUpClass(cls):
        super(TestSaleconsignment, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner = cls.env.ref('base.res_partner_12')
        cls.partner.ref = 1
        cls.product = cls.env['product.product'].create(
            {
                'name': 'Product 1',
                'list_price': 11.0,
                "sale_price": 12.5,
                "indicated_price": 13.75,
                "default_code": "P01",
            }
        )

        cls.so = cls.env['sale.order'].create(
            {
                'esb_ref': 'ref_123',
                'partner_id': cls.partner.id,
                'date_order': '2018-01-29',
                'sale_channel': 'fax',
                'client_order_ref': 'whatever the client want',
                'delivery_price': 23.5,
                'suite_name': '0123434234',
                'order_line': [
                    (
                        0,
                        0,
                        {
                            'sequence': 1,
                            'name': cls.product.name,
                            'product_id': cls.product.id,
                            'product_uom_qty': 7,
                        },
                    )
                ],
            }
        )

    def test_sale_not_consignment(self):
        self.so.action_confirm()
        picking = self.so.picking_ids
        picking.action_confirm()
        picking.action_assign()
        picking.do_prepare_partial()
        # set qty manually as some process in zetes drops it
        picking.pack_operation_ids.qty_done = 7.0
        picking.do_transfer()
        sol = self.so.order_line[0]
        self.assertEqual(sol.qty_delivered, 7.0)
        self.assertEqual(sol.qty_invoiced, 0.0)
        wizard = (
            self.env['stock.return.picking']
            .with_context(active_ids=picking.ids, active_id=picking.id)
            .create({})
        )
        wizard.create_returns()
        wizard.product_return_moves[0].to_refund_so = True
        wizard.product_return_moves[0].quantity = 2.0
        return_pick = picking.browse(wizard.create_returns()["res_id"])
        return_pick.force_assign()
        return_pick.action_assign()
        return_pick.pack_operation_ids.qty_done = 2.0
        return_pick.do_transfer()
        self.assertEqual(sol.qty_delivered, 5.0)
        self.assertEqual(sol.product_qty_returned, 2.0)
        self.assertEqual(sol.qty_invoiced, 0.0)

    def test_sale_is_consignment(self):
        self.so.is_consignment = True
        self.so.action_confirm()
        sol = self.so.order_line[0]
        picking = self.so.picking_ids
        picking.action_confirm()
        picking.action_assign()
        picking.pack_operation_ids.qty_done = 7.0
        picking.do_transfer()
        self.assertEqual(sol.qty_delivered, 0.0)
        self.assertEqual(sol.qty_invoiced, 0.0)

        wizard = (
            self.env['stock.return.picking']
            .with_context(active_ids=picking.ids, active_id=picking.id)
            .create({})
        )
        # return statement doesn't have impact
        wizard.product_return_moves[0].to_refund_so = True
        wizard.product_return_moves[0].quantity = 2.0
        return_pick = picking.browse(wizard.create_returns()["res_id"])
        return_pick.action_assign()
        return_pick.pack_operation_ids.qty_done = 2.0
        return_pick.do_transfer()
        self.assertEqual(sol.qty_delivered, 0.0)
        self.assertEqual(sol.product_qty_returned, 2.0)
