# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase

from .. import constants
from .zetes_test_classes import ZetesTest, DEFAULT_HEADER, \
    ROUND_CODE, PARTNER_NAME
from ..tools.domain_interface import Parameters
from ..tools.domain_assignment import Assignment

OPERATOR_CODE = '99'


class TestAssignemnt(ZetesTest):
    post_install = True
    at_install = False

    def setUp(self):
        super(TestAssignemnt, self).setUp()

        self.env.user.write({
            'tz': 'Europe/Brussels'
        })

        self.picking_zone_medoc = self.env.ref(
            '__setup__.picking_zone_medicament', raise_if_not_found=False)
        if not self.picking_zone_medoc:
            self.picking_zone_medoc = self.env['picking.zone'].create({
                'code': '01',
                'name': 'Medicament',
            })

        # Create a parking Medoc
        reserve_medoc = self.env['stock.location'].create({
            'name': 'Parking Medoc',
            'kind': 'reserve',
            'usage': 'internal',
            'location_id': self.env.ref(
                '__setup__.stock_location_reserve_medoc').id,
            'picking_zone_id': self.picking_zone_medoc.id,
        })
        self.env['stock.location']._parent_store_compute()

        # Set a quantity in this parking
        update_qty_wizard = self.env['stock.change.product.qty'].create({
            'product_id': self.product_1.id,
            'product_tmpl_id': self.product_1.product_tmpl_id.id,
            'new_quantity': 20,
            'location_id': reserve_medoc.id
        })
        update_qty_wizard.change_product_qty()

        self.picking_type_medoc = self.env.ref(
            '__setup__.stock_picking_type_rangement_medoc',
            raise_if_not_found=False)
        if not self.picking_type_medoc:
            wh = self.env.ref('stock.warehouse0')
            internal_sequence = wh.int_type_id.sequence_id
            location_medoc = self.env.ref('__setup__.stock_location_medoc')
            self.picking_type_medoc = self.env['stock.picking.type'].create({
                'name': 'Rangement Medicaments',
                'code': 'internal',
                'sequence_id': internal_sequence.id,
                'default_location_src_id': reserve_medoc.id,
                'default_location_dest_id': location_medoc.id,
                'use_create_lots': False,
                'sequence': 9,
                'picking_zone_id': self.picking_zone_medoc.id,
            })
        reserve_medoc.write({
            'barcode_picking_type_id': self.picking_type_medoc.id,
        })

    def test_requ_assignment(self):
        # Check with no current picking
        domain = Assignment(DEFAULT_HEADER, request_overwrite=self)
        request_params = Parameters(domain, action='requ')
        request_params.update({
            'Cri01': self.picking_zone_medoc.code,
            'Cri02': None,
            'assignmentType': constants.RESERVE_ASSIGNMENT,
            'requestType': '1',
        })

        # Search for a picking
        result_str = domain.requ(request_params)
        result = self.format_result(result_str)
        self.assertEqual(result.respCode, str(constants.RESPONSE_CODE_OK))
        self.assertEqual(result.Usf09, '1')  # Nbr of lines
