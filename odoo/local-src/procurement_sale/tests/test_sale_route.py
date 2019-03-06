# -*- coding: utf-8 -*-
# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestSaleRoute(TransactionCase):
    def setUp(self):
        super(TestSaleRoute, self).setUp()
        self.partner = self.env.ref('base.res_partner_1')
        self.prod1 = self.env.ref('product.product_product_4')
        # Create a sale order
        self.so1 = self.env['sale.order'].create(
            {
                'partner_id': self.partner.id,
                'order_line': [
                    (
                        0,
                        0,
                        {
                            'name': self.prod1.name,
                            'product_id': self.prod1.id,
                            'product_uom': self.ref(
                                'product.product_uom_unit'
                            ),
                            'product_uom_qty': 1,
                            'price_unit': 50,
                        },
                    )
                ],
            }
        )
        # Create a sale route
        self.route = self.env['stock.location.route'].create(
            {'name': 'SO route', 'sale_selectable': True}
        )

    def test_route_change(self):
        """Test procurement update on route change"""
        rules = self.env['exception.rule'].search([('active', '=', 1)])
        rules.write({'active': 0})
        sol = self.so1.order_line[0]
        self.assertEqual(len(sol.procurement_ids), 0)
        self.so1.action_confirm()
        self.assertEqual(len(sol.procurement_ids), 1)
        proc = sol.procurement_ids
        pick = self.so1.picking_ids.filtered(
            lambda p: p.state not in ('cancel', 'waiting')
        )
        self.assertEqual(len(pick), 1)
        moves = pick.filtered(lambda p: p.state not in ('cancel', 'waiting'))
        self.assertEqual(len(moves), 1)
        # Set route on SO line and check procurement has changed
        sol.route_id = self.route
        self.assertEqual(proc.state, 'cancel')
        self.assertEqual(len(sol.procurement_ids), 1)
        proc = sol.procurement_ids
        pick = self.so1.picking_ids.filtered(
            lambda p: p.state not in ('cancel', 'waiting')
        )
        self.assertEqual(len(pick), 1)
        moves = pick.filtered(lambda p: p.state not in ('cancel', 'waiting'))
        self.assertEqual(len(moves), 1)
        # Remove route on SO line and check procurement has changed
        sol.route_id = False
        self.assertEqual(proc.state, 'cancel')
        self.assertEqual(len(sol.procurement_ids), 1)
        pick = self.so1.picking_ids.filtered(
            lambda p: p.state not in ('cancel', 'waiting')
        )
        self.assertEqual(len(pick), 1)
        moves = pick.filtered(lambda p: p.state not in ('cancel', 'waiting'))
        self.assertEqual(len(moves), 1)
        rules.write({'active': 1})
