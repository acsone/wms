# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.tests.common import TransactionCase


class TestStockDeliveryNote(TransactionCase):

    def setUp(self):
        super(TestStockDeliveryNote, self).setUp()
        self.partner = self.env.ref('base.res_partner_1')
        self.product = self.env.ref('product.product_product_1')
        self.supplier_location = self.env.ref('stock.stock_location_suppliers')
        self.destination = self.env.ref('stock.stock_location_customers')
        self.picking = self.env['stock.picking'].create({
            'picking_type_id': self.ref('stock.picking_type_out'),
            'location_id': self.supplier_location.id,
            'location_dest_id': self.destination.id,
            'move_lines': [
                (0, 0, {
                    'name': 'a move',
                    'product_id': self.product.id,
                    'product_uom_qty': 1,
                    'product_uom': self.product.uom_id.id,
                    'location_id': self.supplier_location.id,
                    'location_dest_id': self.destination.id,
                })
            ],
        })

    def test_creation_note_on_validate_picking(self):
        """ """
        self.picking.action_assign()
        pack_operation = self.picking.pack_operation_product_ids
        pack_operation.write({
            'pack_lot_ids': [
                (0, 0, {
                    'life_date': '2017-01-02 10:00:00',
                    'lot_name': '20170102',
                    'qty': 1,
                })
            ],
            'qty_done': 1,
        })
        self.picking.do_new_transfer()
        attachments = self.env['ir.attachment'].search([
            ('res_id', '=', self.picking.id)])
        self.assertEqual(len(attachments), 1)
