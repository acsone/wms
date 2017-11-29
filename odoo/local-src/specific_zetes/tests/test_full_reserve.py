# -*- coding: utf-8 -*-

from .. import constants
from .zetes_test_classes import ZetesParkingTest, DEFAULT_HEADER
from ..tools.domain_interface import Parameters
from ..tools.domain_assignment import Assignment
from ..tools.domain_catchweight import Catchweight
from ..tools.domain_itemmove import Itemmove
from ..tools.domain_location import Location
from ..tools.domain_refdata import Refdata
from ..tools.domain_usercontext import Usercontext


class TestFullReserve(ZetesParkingTest):

    def setUp(self):
        self.disable_picking_validation = True
        super(TestFullReserve, self).setUp()

        # Product 2
        # Location: GAD515
        self.product_2 = self.env['product.product'].create({
            'name': 'Test medoc 2',
            'default_code': '587502',
            'categ_id': self.env.ref('specific_data.product_categ_medoc').id,
            'tracking': 'none',
            'list_price': 5,
        })

        self.location_product_2 = self.env['stock.location'].create({
            'name': 'GD03B2',
            'kind': 'bin',
            'zone': 'G',
            'corridor': 'D',
            'shelf': '03',
            'height': 'B',
            'box': '2',
            'location_id': self.parent_location.id,
            'bin_checksum_1': '45',
            'bin_checksum_2': '45',
        })
        self.env['stock.location']._parent_store_compute()

        # Set a quantity in this parking
        update_qty_wizard = self.env['stock.change.product.qty'].create({
            'product_id': self.product_2.id,
            'product_tmpl_id': self.product_2.product_tmpl_id.id,
            'new_quantity': 20,
            'location_id': self.parking_medoc.id
        })
        update_qty_wizard.change_product_qty()

        self.product_2.write({
            'stock_bin_ids': [(0, 0, {
                'sequence': 1,
                'location_id': self.env.ref('stock.stock_location_stock').id,
                'bin_location_id': self.location_product_2.id,
            })]
        })

        self.reserve_medicament = self.env['stock.location'].create({
            'name': 'GD01F4',
            'kind': 'reserve',
            'zone': 'G',
            'corridor': 'D',
            'shelf': '01',
            'height': 'F',
            'box': '4',
            'location_id': self.parent_location.id,
            'bin_checksum_1': '45',
            'bin_checksum_2': '45',
        })

        self.picking.write({
            'move_lines': [(0, 0, {
                'name': 'Test medoc 2',
                'product_id': self.product_2.id,
                'product_uom_qty': 5,
                'product_uom': self.env.ref('product.product_uom_unit').id,
                'location_id': self.env.ref('stock.stock_location_stock').id,
                'location_dest_id': self.env.ref(
                    'stock.stock_location_output').id,
            })]
        })

        self.picking.action_confirm()
        self.picking.action_assign()
        # Round to the picking
        self.round.button_update()

    def test_full(self):
        assignement_obj = Assignment(DEFAULT_HEADER, request_overwrite=self)
        catchweight_obj = Catchweight(DEFAULT_HEADER, request_overwrite=self)
        itemmove_obj = Itemmove(DEFAULT_HEADER, request_overwrite=self)
        location_obj = Location(DEFAULT_HEADER, request_overwrite=self)
        refdata_obj = Refdata(DEFAULT_HEADER, request_overwrite=self)
        usercontext_obj = Usercontext(DEFAULT_HEADER, request_overwrite=self)

        ##########
        # Step 1 #
        ##########
        login_params = Parameters(usercontext_obj)
        login_params.update({
            'contextType': '1',  # Do a sign in
        })
        result_str = usercontext_obj.requ(login_params)
        result = self.format_result(result_str)
        self.assertEqual(result.respCode, str(constants.RESPONSE_CODE_OK))

        ##########
        # Step 2 #
        ##########
        refdata_params = Parameters(refdata_obj)
        result_str = refdata_obj.requ(refdata_params)
        result_lines = result_str.split('\n')
        results = \
            [self.format_result(result_line) for result_line in result_lines]
        picking_codes = \
            [result_picking.operValue for result_picking in results]
        medic_picking_type = self.picking_type_medoc
        medic_picking_code = medic_picking_type.picking_zone_id.code
        self.assertIn(medic_picking_code, picking_codes)

        ##########
        # Step 3 #
        ##########
        model_name = 'report.stock.quant.bylocation.reserve'
        report = self.env[model_name].search(
            [('product_id', '=', self.product_1.id)],
            limit=1
        )
        self.assertTrue(len(report))

        picking = report.create_reserve_picking()
        self.assertEqual(len(picking.pack_operation_product_ids), 1)

        request_picking_params = Parameters(assignement_obj)
        request_picking_params.update({
            'assignmentType': constants.RESERVE_ASSIGNMENT,
            'requestType': '1',
            'tripCounter': '1',
            'Cri01': medic_picking_code,
            'Cri02': None,
        })
        result_str = assignement_obj.requ(request_picking_params)
        result = self.format_result(result_str)
        self.assertEqual(result.respCode, str(constants.RESPONSE_CODE_OK))

        self.assertEqual(result.groupNum, str(picking.id))
        self.assertEqual(result.Usf09, '1')

        start_picking_params = Parameters(assignement_obj)
        start_picking_params.update({
            'groupNum': picking.id,
            'assignmentStatus': constants.AS_START,

        })
        assignement_obj.resu(start_picking_params)
        self.assertEqual(picking.operator_id.id, self.user.id)

        ##########
        # Step 4 #
        ##########
        itemmove_params = Parameters(itemmove_obj)
        itemmove_params.update({
            'groupNum': picking.id,
            'itemMoveType': constants.MOVE_TYPE_PUT,
            'Cri01': '0',
        })
        result_str = itemmove_obj.requ(itemmove_params)
        result_lines = result_str.split('\n')
        results = \
            [self.format_result(result_line) for result_line in result_lines]
        self.assertEqual(len(results), 1)
        line_product_1 = results[0]

        # One line:
        # 15 units of product 1 to move from reserve to stock

        # Test line 1
        self.assertFalse(line_product_1.Usf02)
        self.assertEqual(line_product_1.productCode,
                         self.product_2.default_code)
        self.assertEqual(int(line_product_1.reqQty), 20)
        self.assertFalse(int(line_product_1.moveLineId))

        validate_pick_items_params = Parameters(catchweight_obj)
        validate_pick_items_params.update({
            'groupNum': picking.id,
            'lineId': line_product_2.moveLineId,
            'Usf01': self.lot_product_1.checksum,
            'Usf02': 75,  # Pick 75 items
            'Usf03': None,
        })

        catchweight_obj.resu(validate_pick_items_params)
        self.assertEqual(pack_op_1.qty_done, 75)

        request_validate_picking_line_request = Parameters(itemmove_obj)
        request_validate_picking_line_request.update({
            'groupNum': picking.id,
            'moveLineId': line_product_2.moveLineId,
            'moveStatus': constants.MOVE_FULL,
        })

        itemmove_obj.resu(request_validate_picking_line_request)
        self.assertEqual(pack_op_1.zetes_state, constants.MOVE_FULL)

        ##########
        # Step 7 #
        ##########
        # Now the picker have to go to the reserve
        request_location_param = Parameters(location_obj)
        request_location_param.update({
            'lineId': line_product_2.moveLineId,
            'Cri01': self.reserve_medicament.zone,
            'Cri02': self.reserve_medicament.corridor,
            'Cri03': self.reserve_medicament.shelf,
            'Cri04': self.reserve_medicament.height,
            'Cri05': self.reserve_medicament.box,
            'Cri07': None,
        })
        result_str = location_obj.requ(request_location_param)
        result = self.format_result(result_str)

        self.assertEqual(result.respCode, str(constants.RESPONSE_CODE_OK))
        self.assertEqual(result.lC1, str(self.reserve_medicament.zone))

        ##########
        # Step 8 #
        ##########
        # The picker put 25 units of product 1 in the reserve
        validate_reserve_qty_params = Parameters(catchweight_obj)
        validate_reserve_qty_params.update({
            'groupNum': picking.id,
            'lineId': line_product_2.moveLineId,
            'Usf01': self.lot_product_1.checksum,
            'Usf02': 25,  # Pick 25 items
            'Usf03': None,
        })
        catchweight_obj.resu(validate_reserve_qty_params)

        self.assertEqual(len(picking.pack_operation_product_ids), 3)
        self.assertEqual(pack_op_1.product_qty, 75)
        self.assertEqual(pack_op_1.qty_done, 75)
        new_pack_op = picking.pack_operation_product_ids.filtered(
            lambda line:
            line.product_id.id == self.product_1.id and
            line.location_dest_id.id == self.reserve_medicament.id)
        self.assertEqual(len(new_pack_op), 1)
        self.assertEqual(new_pack_op.product_qty, 25)
        self.assertEqual(new_pack_op.qty_done, 25)

        validate_line_params = Parameters(itemmove_obj)
        validate_line_params.update({
            'moveLineId': line_product_2.moveLineId,
            'moveStatus': constants.MOVE_DONE,
        })
        itemmove_obj.resu(validate_line_params)

        ##########
        # Step 9 #
        ##########
        # The picker put 15 units of product 2 in the stock
        validate_pick_items_params = Parameters(catchweight_obj)
        validate_pick_items_params.update({
            'groupNum': picking.id,
            'lineId': line_product_3.moveLineId,
            'Usf01': None,
            'Usf02': 15,  # Pick 15 items
            'Usf03': None,
        })

        catchweight_obj.resu(validate_pick_items_params)
        self.assertEqual(pack_op_2.qty_done, 15)

        request_validate_picking_line_request = Parameters(itemmove_obj)
        request_validate_picking_line_request.update({
            'groupNum': picking.id,
            'moveLineId': line_product_3.moveLineId,
            'moveStatus': constants.MOVE_DONE,
        })

        itemmove_obj.resu(request_validate_picking_line_request)
        self.assertEqual(pack_op_2.zetes_state, constants.MOVE_DONE)
        self.assertEqual(pack_op_2.product_qty, 15)
        self.assertEqual(pack_op_2.qty_done, 15)

        validate_line_params = Parameters(itemmove_obj)
        validate_line_params.update({
            'moveLineId': line_product_3.moveLineId,
            'moveStatus': constants.MOVE_DONE,
        })
        itemmove_obj.resu(validate_line_params)

        ###########
        # Step 10 #
        ###########
        # The picking is now finished and validated
        request_finish_picking_params = Parameters(assignement_obj)
        request_finish_picking_params.update({
            'groupNum': picking.id,
            'assignmentStatus': constants.AS_DONE,
            'Usf01': 1
        })

        assignement_obj.resu(request_finish_picking_params)
        self.assertEqual(picking.state, 'done')
