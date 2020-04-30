# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class GroupByPartnerCommonCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(GroupByPartnerCommonCase, cls).setUpClass()

        # workaround for active sale exceptions making tests fail
        if 'exception.rule' in cls.env:
            cls.env['exception.rule'].search([]).write({'active': False})

        cls.partner1 = cls.env['res.partner'].create(
            {'name': 'Unittest partner', 'ref': '12344566777878'}
        )
        cls.p1 = cls.env['product.product'].create(
            {
                'name': 'Unittest P1',
                'uom_id': cls.env.ref('product.product_uom_unit').id,
                'type': 'product',
                'weight': 10.0,
            }
        )
        cls.carrier_fixed = cls.env['delivery.carrier'].create(
            {
                'name': 'Unittest shipping costs',
                'delivery_type': 'fixed',
                'fixed_price': 10.0,
            }
        )
        cls.warehouse_1 = cls.env['stock.warehouse'].create(
            {
                'name': 'Base Warehouse',
                'reception_steps': 'one_step',
                'delivery_steps': 'pick_ship',
                'code': 'BWH',
            }
        )
        warehouse = cls.warehouse_1
        warehouse.pick_type_id.groupbypartner = True
        warehouse.pick_type_id.subcode = 'PICK'
