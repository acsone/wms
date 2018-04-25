# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.tests.common import TransactionCase


class TestCreateTicketWizard(TransactionCase):

    def setUp(self):
        super(TestCreateTicketWizard, self).setUp()
        self.reason_defect = self.env.ref('specific_helpdesk.product_defect')
        self.partner1 = self.env['res.partner'].create({
            'name': 'Partner One',
            })
        self.p1 = self.env['product.product'].create({
             'name': 'Unittest P1',
             'uom_id': self.ref('product.product_uom_unit'),
             'type': 'consu',
             })
        self.so1 = self.env['sale.order'].create({
             'partner_id': self.partner1.id,
             'order_line': [
                 (0, 0, {
                     'name': self.p1.name,
                     'product_id': self.p1.id,
                     'product_uom': self.ref('product.product_uom_unit'),
                     'product_uom_qty': 1,
                     'price_unit': 50,
                 }),
             ]
         })
        self.so1.action_confirm()
        self.picking = self.so1.picking_ids[0]

    def test_get_wizard_to_create_ticket(self):
        """Test we get the wizard to create tickets."""
        r = self.env['create.helpdesk.ticket'].create({
            'stock_picking_id': self.picking.id
        })
        w = self.env['helpdesk.ticket'].new_one(r)
        self.assertEqual(w['res_id'], r.id)

    def test_create_ticket_for_stock_picking(self):
        """Create a new ticket for a picking with the wizard model"""
        r = self.env['create.helpdesk.ticket'].create({
            'stock_picking_id': self.picking.id
        })
        r.helpdesk_ticket_reason_id = self.reason_defect
        r.description = 'Test ticket'
        new_ticket = r.with_context(
                active_id=self.picking.id,
                active_model='stock.picking').create_helpdesk_ticket()
        new_ticket = self.env['helpdesk.ticket'].search(
                [(1, '=', 1)], order='id desc', limit=1)
        self.assertEqual(new_ticket.helpdesk_ticket_reason_id,
                         self.reason_defect)
        self.assertEqual(new_ticket.name, r.description)
        self.assertEqual(new_ticket.stock_picking_id, self.picking)
        self.assertEqual(new_ticket.sale_order_id, self.so1)
