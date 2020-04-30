# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo.tests.common import SavepointCase


class TestCreateTicketWizard(SavepointCase):
    at_install = False
    post_install = True

    @classmethod
    def setUpClass(cls):
        super(TestCreateTicketWizard, cls).setUpClass()
        cls.reason_defect = cls.env.ref('specific_helpdesk.product_defect')
        cls.partner1 = cls.env['res.partner'].create(
            {'name': 'Partner One', 'ref': '99829422054'}
        )
        cls.p1 = cls.env['product.product'].create(
            {
                'name': 'Unittest P1',
                'uom_id': cls.env.ref('product.product_uom_unit').id,
                'type': 'consu',
            }
        )
        cls.so1 = cls.env['sale.order'].create(
            {
                'partner_id': cls.partner1.id,
                'order_line': [
                    (
                        0,
                        0,
                        {
                            'name': cls.p1.name,
                            'product_id': cls.p1.id,
                            'product_uom': cls.env.ref(
                                'product.product_uom_unit'
                            ).id,
                            'product_uom_qty': 1,
                            'price_unit': 50,
                        },
                    )
                ],
            }
        )
        cls.so1.action_confirm()
        cls.picking = cls.so1.picking_ids[0]

    def test_get_wizard_to_create_ticket(self):
        """Test we get the wizard to create tickets."""
        r = self.env['create.helpdesk.ticket'].create({})
        w = self.env['helpdesk.ticket'].new_one(r)
        self.assertEqual(w['res_id'], r.id)

    def test_create_ticket_for_stock_picking(self):
        """Create a new ticket for a picking with the wizard model"""
        r = self.env['create.helpdesk.ticket'].create({})
        r.helpdesk_ticket_reason_id = self.reason_defect
        r.description = 'Test ticket'
        r.with_context(
            active_id=self.picking.id, active_model='stock.picking'
        ).create_helpdesk_ticket()
        new_ticket = self.env['helpdesk.ticket'].search(
            [(1, '=', 1)], order='id desc', limit=1
        )
        self.assertEqual(
            new_ticket.helpdesk_ticket_reason_id, self.reason_defect
        )
        self.assertEqual(new_ticket.name, r.description)
        self.assertEqual(new_ticket.stock_picking_id, self.picking)
        self.assertEqual(new_ticket.sale_order_id, self.so1)
