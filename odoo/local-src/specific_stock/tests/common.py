# -*- coding: utf-8 -*-
# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class BaseCase(TransactionCase):
    def setUp(self):
        super(BaseCase, self).setUp()
        self.env = self.env(
            context=dict(self.env.context, tracking_disable=True)
        )

        self.product_1 = self.env['product.product'].create(
            {
                'name': 'Product 1',
                'type': 'product',
                'uom_id': self.env.ref('product.product_uom_unit').id,
                'uom_po_id': self.env.ref('product.product_uom_unit').id,
                'default_code': 'TOR1',
                'tracking': 'lot',
            }
        )
        self.product_1_lotA = self.env['stock.production.lot'].create(
            {'product_id': self.product_1.id, 'name': 'LotA'}
        )
        self.product_1_lotB = self.env['stock.production.lot'].create(
            {'product_id': self.product_1.id, 'name': 'LotB'}
        )
        self.product_1_add = self.env['product.product'].create(
            {
                'name': 'Product 1 add',
                'type': 'product',
                'uom_id': self.env.ref('product.product_uom_unit').id,
                'uom_po_id': self.env.ref('product.product_uom_unit').id,
                'default_code': 'TOR1ADD',
            }
        )
        self.product_1.write(
            {
                'additional_product_id': self.product_1_add.id,
                'ratio_main_product': 1,
                'ratio_additional_product': 1,
            }
        )
        self.product_2 = self.env['product.product'].create(
            {
                'name': 'Product 2',
                'type': 'product',
                'uom_id': self.env.ref('product.product_uom_unit').id,
                'uom_po_id': self.env.ref('product.product_uom_unit').id,
                'default_code': 'TOR2',
            }
        )

        wh = self.env['stock.warehouse'].search([])
        self.location = wh[0].view_location_id
        self.location.usage = 'internal'
        self.loc_customer = self.env.ref('stock.stock_location_customers')

        self.pick_type = self.env.ref('stock.picking_type_out')
        self.pick_type.subcode = 'PICK'
