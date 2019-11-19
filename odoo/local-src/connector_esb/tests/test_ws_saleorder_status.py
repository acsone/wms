# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from copy import deepcopy
from datetime import datetime

from odoo.tests.common import SavepointCase


class WSSaleOrderStatusTestCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(WSSaleOrderStatusTestCase, cls).setUpClass()

        cls.partner = cls.env['res.partner'].create(
            {'name': 'Partner 1', 'ref': '93765921390'}
        )

        cls.prod1 = cls.env['product.product'].create(
            {
                'name': 'Product 1',
                'default_code': 'ref1',
                'cnk_code': '000015',
                'sale_ok': True,
                'type': 'product',
            }
        )

        cls.prod2 = cls.env['product.product'].create(
            {
                'name': 'Product 2',
                'default_code': 'ref2',
                'cnk_code': '000062',
                'sale_ok': True,
                'type': 'product',
            }
        )

        cls.order_data = {
            'order_ref': 'ref_123',
            'increment_id': 'INC-ID',
            'customer_id': cls.partner.ref,
            'date': '2018-08-05 15:23:12',
            'lines': [
                {'line_id': 1, 'cnk': cls.prod1.cnk_code, 'quantity': 20},
                {'line_id': 2, 'cnk': cls.prod2.cnk_code, 'quantity': 5},
            ],
        }

    def test_saleorder_status(self):
        """ Test the method sale order status with a standard SO """

        data = deepcopy(self.order_data)
        self.so0 = self.env['sale.order']._ws_create_new(data, datetime.now())
        self.so0.action_confirm()

        partner_ref = self.partner.ref
        esb_ref = self.so0.esb_ref

        backend = self.env['esb.backend'].get_singleton()
        with backend.work_on('sale.order') as work:
            component = work.component('ws.message.sale.order.status')
            result = component.get_message(partner_ref, esb_ref)

        self.assertEqual(result['state'], 'sale')
        self.assertEqual(result['price_subtotal'], 25)
        self.assertEqual(result['price_tax'], 5.25)
        self.assertEqual(result['price_total'], 30.25)
        self.assertEqual(len(result['lines']), 2)

    def test_saleorder_status_with_wrong_product(self):
        """ Test the method sale order status with a wrong product

        For outside partners (currently hardcoded to
        partner_ref in ('8114', '8264') with a quick dirty fix.
        """
        # Create a rule to ban product that cannot be sold (sale_ok == False)
        self.env['exception.rule'].search([]).unlink()
        rule = self.env['exception.rule'].create(
            {
                'name': 'Test if can be sold',
                'description': 'This product cannot be sold',
                'model': 'sale.order.line',
                'code': "failed = not object.product_id.sale_ok",
                'active': True,
            }
        )

        self.prod2.sale_ok = False

        data = deepcopy(self.order_data)
        data['customer_id'] = '8114'
        self.partner.ref = '8114'
        self.so0 = self.env['sale.order']._ws_create_new(data, datetime.now())
        self.so0.action_confirm()

        partner_ref = self.partner.ref
        esb_ref = self.so0.esb_ref

        # Compute exceptions
        self.assertTrue(self.so0.ignore_exception)

        backend = self.env['esb.backend'].get_singleton()
        with backend.work_on('sale.order') as work:
            component = work.component('ws.message.sale.order.status')
            result = component.get_message(partner_ref, esb_ref)

        self.assertEqual(result['state'], 'sale')
        self.assertEqual(result['price_total'], 24.2)
        self.assertEqual(len(result['lines']), 2)

        good_line = [l for l in result['lines'] if l['cnk'] == '000015']
        wrong_line = [l for l in result['lines'] if l['cnk'] == '000062']

        self.assertEqual(len(good_line), 1)
        self.assertEqual(len(wrong_line), 1)

        # Check the good line
        good_line = good_line[0]
        self.assertEqual(good_line['quantity'], 20)
        self.assertIsNone(good_line['error'])

        wrong_line = wrong_line[0]
        self.assertEqual(wrong_line['quantity'], 0)
        self.assertEqual(wrong_line['error'], rule.description)

    def test_saleorder_status_with_wrong_product_from_esb(self):
        """ Test the method sale order status with a wrong product

        From trusted source, we don't set quantities to 0
        parole from ESB is considered holy
        (doesn't mean it can't be wrong but then as we want to be in
        sync we want to reproduce the same holy errors too)
        """
        # Create a rule to ban product that cannot be sold (sale_ok == False)
        self.env['exception.rule'].search([]).unlink()
        rule = self.env['exception.rule'].create(
            {
                'name': 'Test if can be sold',
                'description': 'This product cannot be sold',
                'model': 'sale.order.line',
                'code': "failed = not object.product_id.sale_ok",
                'active': True,
            }
        )

        self.prod2.sale_ok = False

        data = deepcopy(self.order_data)
        self.so0 = self.env['sale.order']._ws_create_new(data, datetime.now())
        self.so0.action_confirm()

        partner_ref = self.partner.ref
        esb_ref = self.so0.esb_ref

        # Compute exceptions
        self.assertTrue(self.so0.ignore_exception)

        backend = self.env['esb.backend'].get_singleton()
        with backend.work_on('sale.order') as work:
            component = work.component('ws.message.sale.order.status')
            result = component.get_message(partner_ref, esb_ref)

        self.assertEqual(result['state'], 'sale')
        self.assertEqual(result['price_total'], 30.25)
        self.assertEqual(len(result['lines']), 2)

        good_line = [l for l in result['lines'] if l['cnk'] == '000015']
        wrong_line = [l for l in result['lines'] if l['cnk'] == '000062']

        self.assertEqual(len(good_line), 1)
        self.assertEqual(len(wrong_line), 1)

        # Check the good line
        good_line = good_line[0]
        self.assertEqual(good_line['quantity'], 20)
        self.assertIsNone(good_line['error'])

        wrong_line = wrong_line[0]
        self.assertEqual(wrong_line['quantity'], 5)
        self.assertEqual(wrong_line['error'], rule.description)
