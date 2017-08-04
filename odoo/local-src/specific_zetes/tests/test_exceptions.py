# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import fields

from .. import constants
from .zetes_test_classes import ZetesTest, DEFAULT_HEADER
from ..tools.domain_interface import Parameters
from ..tools.domain_assignment import Assignment
from ..tools.domain_catchweight import Catchweight
from ..tools.domain_itempick import Itempick
from ..tools.domain_usercontext import Usercontext


class TestExceptions(ZetesTest):

    def setUp(self):
        self.disable_picking_validation = True
        super(TestExceptions, self).setUp()

        # Product 2
        # Location: GAD515
        self.product_2 = self.env['product.product'].create({
            'name': 'Test medoc 2',
            'default_code': '587502',
            'categ_id': self.env.ref('specific_data.product_categ_medoc').id,
            'tracking': 'lot',
            'list_price': 40,
        })

        self.location_product_2 = self.env['stock.location'].create({
            'name': 'GAD515',
            'kind': 'bin',
            'zone': 'G',
            'corridor': 'A',
            'shelf': 'D',
            'height': '5',
            'box': '15',
            'location_id': self.parent_location.id,
            'bin_checksum_1': '456',
            'bin_checksum_2': '456',
        })
        self.env['stock.location']._parent_store_compute()

        two_years = datetime.now() + relativedelta(years=2)
        self.lot_product_2 = self.env['stock.production.lot'].create({
            'name': '000000001',
            'product_id': self.product_2.id,
            'life_date': fields.Datetime.to_string(two_years),
        })
        update_qty_wizard = self.env['stock.change.product.qty'].create({
            'product_id': self.product_2.id,
            'product_tmpl_id': self.product_1.product_tmpl_id.id,
            'new_quantity': 10,
            'lot_id': self.lot_product_2.id,
            'location_id': self.location_product_2.id
        })
        update_qty_wizard.change_product_qty()

        self.picking.write({
            'move_lines': [(0, 0, {
                'name': 'Test medoc 2',
                'product_id': self.product_2.id,
                'product_uom_qty': 10,
                'product_uom': self.env.ref('product.product_uom_unit').id,
                'location_id': self.env.ref('stock.stock_location_stock').id,
                'location_dest_id': self.env.ref(
                    'stock.stock_location_output').id,
            })]
        })

        self.picking.action_assign()

    def test_exceptions(self):
        """
        Please read the README file to understand the test
        :return:
        """

        assignement_obj = Assignment(DEFAULT_HEADER, request_overwrite=self)
        catchweight_obj = Catchweight(DEFAULT_HEADER, request_overwrite=self)
        itempick_obj = Itempick(DEFAULT_HEADER, request_overwrite=self)
        usercontext_obj = Usercontext(DEFAULT_HEADER, request_overwrite=self)

        ##########
        # Step 1 #
        ##########
        # Start the picking
        start_picking_params = Parameters(assignement_obj)
        start_picking_params.update({
            'groupNum': self.picking.id,
            'assignmentStatus': constants.AS_START,

        })
        assignement_obj.resu(start_picking_params)

        move_1 = self.picking.pack_operation_product_ids[0]
        move_2 = self.picking.pack_operation_product_ids[1]

        ##########
        # Step 2 #
        ##########
        # Pick 10 items for the first move
        request_pick_items_params = Parameters(catchweight_obj)
        request_pick_items_params.update({
            'groupNum': self.picking.id,
            'lineId': move_1.id,
            'Usf01': self.lot_product_1.checksum,
            'Usf02': 10,  # Pick 10 items
        })
        catchweight_obj.resu(request_pick_items_params)

        request_validate_picking_line_params = Parameters(itempick_obj)
        request_validate_picking_line_params.update({
            'groupNum': self.picking.id,
            'pickLineId': move_1.id,
            'pickStatus': constants.OP_PICKED,
        })
        itempick_obj.resu(request_validate_picking_line_params)

        ##########
        # Step 3 #
        ##########
        login_params = Parameters(usercontext_obj)
        login_params.update({
            'contextType': '1',  # Do a sign in
        })
        result_str = usercontext_obj.requ(login_params)
        result = self.format_result(result_str)
        self.assertEqual(result.respCode, str(constants.RESPONSE_CODE_OK))
        self.assertEqual(result.unitSlam, '1')
        self.assertEqual(result.Usf01, str(self.picking.id))

        request_restart_picking_params = Parameters(assignement_obj)
        request_restart_picking_params.update({
            'groupNum': self.picking.id,
            'assignmentStatus': constants.AS_START
        })
        assignement_obj.resu(request_restart_picking_params)

        ##########
        # Step 4 #
        ##########
        request_picking_line_params = Parameters(itempick_obj)
        request_picking_line_params.update({
            'groupNum': self.picking.id,
            'Cri01': 0
        })

        result_str = itempick_obj.requ(request_picking_line_params)
        result_lines = result_str.split('\n')
        results = \
            [self.format_result(result_line) for result_line in result_lines]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].pickLineId, str(move_2.id))
