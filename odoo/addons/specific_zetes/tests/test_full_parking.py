# -*- coding: utf-8 -*-
import unittest

import mock

from .. import constants
from ..tools.domain_assignment import Assignment
from ..tools.domain_catchweight import Catchweight
from ..tools.domain_interface import Parameters
from ..tools.domain_itemmove import Itemmove
from ..tools.domain_location import Location
from ..tools.domain_refdata import Refdata
from ..tools.domain_usercontext import Usercontext
from .zetes_test_classes import ZetesParkingTest


class TestFullParking(ZetesParkingTest):
    def setUp(self):
        self.disable_picking_validation = True
        super(TestFullParking, self).setUp()

        self.location_product_2 = self.env['stock.location'].create(
            {
                'name': 'GD80B2',
                'kind': 'bin',
                'zone': 'G',
                'corridor': 'D',
                'shelf': '80',
                'height': 'B',
                'box': '2',
                'location_id': self.zone_gustave.id,
                'bin_checksum_1': '45',
                'bin_checksum_2': '45',
            }
        )
        self.env['stock.location']._parent_store_compute()

        # Product 2
        # Location: GD80B2
        self.product_2 = self.env['product.product'].create(
            {
                'name': 'Test medoc 2',
                'default_code': '587502',
                'categ_id': self.product_categ_medoc.id,
                'tracking': 'none',
                'list_price': 5,
                'type': 'product',
                'stock_bin_ids': [
                    (
                        0,
                        0,
                        {
                            'sequence': 1,
                            'location_id': self.stock_location.id,
                            'bin_location_id': self.location_product_2.id,
                        },
                    )
                ],
            }
        )

        # Set a quantity in this parking
        update_qty_wizard = self.env['stock.change.product.qty'].create(
            {
                'product_id': self.product_2.id,
                'product_tmpl_id': self.product_2.product_tmpl_id.id,
                'new_quantity': 20,
                'location_id': self.parking_medoc.id,
            }
        )
        update_qty_wizard.change_product_qty()

        self.reserve_medicament = self.env['stock.location'].create(
            {
                'name': 'GD80F4',
                'kind': 'reserve',
                'zone': 'G',
                'corridor': 'D',
                'shelf': '80',
                'height': 'F',
                'box': '4',
                'location_id': self.zone_gustave.id,
                'bin_checksum_1': '45',
                'bin_checksum_2': '45',
            }
        )

        self.picking.write(
            {
                'move_lines': [
                    (
                        0,
                        0,
                        {
                            'name': 'Test medoc 2',
                            'product_id': self.product_2.id,
                            'product_uom_qty': 5,
                            'product_uom': self.env.ref(
                                'product.product_uom_unit'
                            ).id,
                            'location_id': self.env.ref(
                                'stock.stock_location_stock'
                            ).id,
                            'location_dest_id': self.env.ref(
                                'stock.stock_location_output'
                            ).id,
                        },
                    )
                ]
            }
        )

        self.picking.action_confirm()
        self.picking.action_assign()
        # Round to the picking
        self.round.button_update()

    @unittest.skip(
        "Test is failing randomly, see "
        "https://github.com/camptocamp/alcyon_odoo/issues/1097"
    )
    def test_full(self):
        assignement_obj = Assignment(
            self._default_header(), mock.MagicMock(name='Savepoint()')
        )
        catchweight_obj = Catchweight(
            self._default_header(), mock.MagicMock(name='Savepoint()')
        )
        itemmove_obj = Itemmove(
            self._default_header(), mock.MagicMock(name='Savepoint()')
        )
        location_obj = Location(
            self._default_header(), mock.MagicMock(name='Savepoint()')
        )
        refdata_obj = Refdata(
            self._default_header(), mock.MagicMock(name='Savepoint()')
        )
        usercontext_obj = Usercontext(
            self._default_header(), mock.MagicMock(name='Savepoint()')
        )

        ##########
        # Step 1 #
        ##########
        login_params = Parameters(usercontext_obj)
        login_params.update({'contextType': '1'})  # Do a sign in
        result_str = usercontext_obj.requ(login_params)
        result = self.format_result(result_str)
        self.assertEqual(result.respCode, str(constants.RESPONSE_CODE_OK))

        ##########
        # Step 2 #
        ##########
        refdata_params = Parameters(refdata_obj)
        result_str = refdata_obj.requ(refdata_params)
        result_lines = result_str.split('\n')
        results = [
            self.format_result(result_line) for result_line in result_lines
        ]
        picking_codes = [
            result_picking.operValue for result_picking in results
        ]
        medic_picking_type = self.picking_type_medoc
        medic_picking_code = medic_picking_type.picking_zone_id.code
        self.assertIn(medic_picking_code, picking_codes)

        ##########
        # Step 3 #
        ##########
        model_name = 'report.stock.refill.arrange'
        report = self.env[model_name].search(
            [('product_id', '=', self.product_1.id)], limit=1
        )
        self.assertTrue(len(report))

        picking = report.create_picking()
        self.assertEqual(len(picking.pack_operation_product_ids), 2)

        request_picking_params = Parameters(assignement_obj)
        request_picking_params.update(
            {
                'assignmentType': constants.RANGEMENT_ASSIGNMENT,
                'requestType': '1',
                'tripCounter': '1',
                'Cri01': medic_picking_code,
                'Cri02': None,
            }
        )
        result_str = assignement_obj.requ(request_picking_params)
        result = self.format_result(result_str)
        self.assertEqual(result.respCode, str(constants.RESPONSE_CODE_OK))

        self.assertEqual(result.groupNum, str(picking.id))
        self.assertEqual(result.Usf09, '2')

        start_picking_params = Parameters(assignement_obj)
        start_picking_params.update(
            {'groupNum': picking.id, 'assignmentStatus': constants.AS_START}
        )
        assignement_obj.resu(start_picking_params)
        self.assertEqual(picking.operator_id.id, self.operator_user.id)

        ##########
        # Step 4 #
        ##########
        itemmove_params = Parameters(itemmove_obj)
        itemmove_params.update(
            {
                'groupNum': picking.id,
                'itemMoveType': constants.MOVE_TYPE_LOAD,
                'Cri01': '0',
            }
        )
        result_str = itemmove_obj.requ(itemmove_params)
        result_lines = result_str.split('\n')
        results = [
            self.format_result(result_line) for result_line in result_lines
        ]
        self.assertEqual(len(results), 3)
        line_product_1 = results[0]
        line_product_2 = results[1]
        line_product_3 = results[2]

        # Three lines:
        # 5 of product 2 to unload (reserved)
        # 100 of product 1 to load in stock
        # 15 of product 2 to load in stock

        # Test line 1
        self.assertEqual(line_product_1.Usf02, constants.MOVE_UNLOAD)
        self.assertEqual(
            line_product_1.productCode, self.product_2.default_code
        )
        self.assertEqual(int(line_product_1.reqQty), 5)
        self.assertFalse(int(line_product_1.moveLineId))

        # Test line 2
        pack_op_1 = picking.pack_operation_product_ids.filtered(
            lambda rec: rec.product_id == self.product_1
        )
        self.assertEqual(line_product_2.Usf02, constants.MOVE_LOAD)
        self.assertEqual(
            line_product_2.productCode, self.product_1.default_code
        )
        self.assertEqual(int(line_product_2.reqQty), 100)
        self.assertEqual(
            line_product_2.moveLineId,
            "{}_{}".format(pack_op_1.id, self.lot_product_1.id),
        )

        # Test line 3
        pack_op_2 = picking.pack_operation_product_ids.filtered(
            lambda rec: rec.product_id == self.product_2
        )
        self.assertEqual(line_product_3.Usf02, constants.MOVE_LOAD)
        self.assertEqual(
            line_product_3.productCode, self.product_2.default_code
        )
        self.assertEqual(int(line_product_3.reqQty), 15)
        self.assertEqual(int(line_product_3.moveLineId), pack_op_2.id)

        ##########
        # Step 5 #
        ##########
        # Unload 5 units from product 2
        resu_catchweight_params = Parameters(catchweight_obj)
        resu_catchweight_params.update(
            {
                'groupNum': picking.id,
                'pickLineId': line_product_1.moveLineId,
                'effQty': 5,
            }
        )

        ##########
        # Step 6 #
        ##########
        # The picker can only put 75 units of product 1 in the bin
        validate_pick_items_params = Parameters(catchweight_obj)
        validate_pick_items_params.update(
            {
                'groupNum': picking.id,
                'lineId': line_product_2.moveLineId,
                'Usf01': self.lot_product_1.voice_identifier,
                'Usf02': 75,  # Pick 75 items
                'Usf03': None,
            }
        )

        catchweight_obj.resu(validate_pick_items_params)
        self.assertEqual(pack_op_1.qty_done, 75)

        request_validate_picking_line_request = Parameters(itemmove_obj)
        request_validate_picking_line_request.update(
            {
                'groupNum': picking.id,
                'moveLineId': line_product_2.moveLineId,
                'moveStatus': constants.MOVE_FULL,
                'itemMoveType': constants.MOVE_TYPE_LOAD,
            }
        )

        itemmove_obj.resu(request_validate_picking_line_request)
        self.assertEqual(pack_op_1.zetes_state, constants.MOVE_FULL)

        ##########
        # Step 7 #
        ##########
        # Now the picker have to go to the reserve
        request_location_param = Parameters(location_obj)
        request_location_param.update(
            {
                'lineId': line_product_2.moveLineId,
                'Cri01': self.reserve_medicament.zone,
                'Cri02': self.reserve_medicament.corridor,
                'Cri03': self.reserve_medicament.shelf,
                'Cri04': self.reserve_medicament.height,
                'Cri05': self.reserve_medicament.box,
                'Cri07': None,
            }
        )
        result_str = location_obj.requ(request_location_param)
        result = self.format_result(result_str)

        self.assertEqual(result.respCode, str(constants.RESPONSE_CODE_OK))
        self.assertEqual(result.lC1, str(self.reserve_medicament.zone))

        ##########
        # Step 8 #
        ##########
        # The picker put 25 units of product 1 in the reserve
        validate_reserve_qty_params = Parameters(catchweight_obj)
        validate_reserve_qty_params.update(
            {
                'groupNum': picking.id,
                'lineId': line_product_2.moveLineId,
                'Usf01': self.lot_product_1.voice_identifier,
                'Usf02': 25,  # Pick 25 items
                'Usf03': None,
            }
        )
        catchweight_obj.resu(validate_reserve_qty_params)

        self.assertEqual(len(picking.pack_operation_product_ids), 3)
        self.assertEqual(pack_op_1.product_qty, 75)
        self.assertEqual(pack_op_1.qty_done, 75)
        new_pack_op = picking.pack_operation_product_ids.filtered(
            lambda line: line.product_id.id == self.product_1.id
            and line.location_dest_id.id == self.reserve_medicament.id
        )
        self.assertEqual(len(new_pack_op), 1)
        self.assertEqual(new_pack_op.product_qty, 25)
        self.assertEqual(new_pack_op.qty_done, 25)

        validate_line_params = Parameters(itemmove_obj)
        validate_line_params.update(
            {
                'moveLineId': line_product_2.moveLineId,
                'moveStatus': constants.MOVE_DONE,
                'itemMoveType': constants.MOVE_TYPE_LOAD,
            }
        )
        itemmove_obj.resu(validate_line_params)

        ##########
        # Step 9 #
        ##########
        # The picker put 15 units of product 2 in the stock
        validate_pick_items_params = Parameters(catchweight_obj)
        validate_pick_items_params.update(
            {
                'groupNum': picking.id,
                'lineId': line_product_3.moveLineId,
                'Usf01': None,
                'Usf02': 15,  # Pick 15 items
                'Usf03': None,
            }
        )

        catchweight_obj.resu(validate_pick_items_params)
        self.assertEqual(pack_op_2.qty_done, 15)

        request_validate_picking_line_request = Parameters(itemmove_obj)
        request_validate_picking_line_request.update(
            {
                'groupNum': picking.id,
                'moveLineId': line_product_3.moveLineId,
                'moveStatus': constants.MOVE_DONE,
                'itemMoveType': constants.MOVE_TYPE_LOAD,
            }
        )

        itemmove_obj.resu(request_validate_picking_line_request)
        self.assertEqual(pack_op_2.zetes_state, constants.MOVE_DONE)
        self.assertEqual(pack_op_2.product_qty, 15)
        self.assertEqual(pack_op_2.qty_done, 15)

        validate_line_params = Parameters(itemmove_obj)
        validate_line_params.update(
            {
                'moveLineId': line_product_3.moveLineId,
                'moveStatus': constants.MOVE_DONE,
                'itemMoveType': constants.MOVE_TYPE_LOAD,
            }
        )
        itemmove_obj.resu(validate_line_params)

        ###########
        # Step 10 #
        ###########
        # The picking is now finished and validated
        request_finish_picking_params = Parameters(assignement_obj)
        request_finish_picking_params.update(
            {
                'groupNum': picking.id,
                'assignmentStatus': constants.AS_DONE,
                'Usf01': 1,
            }
        )

        assignement_obj.resu(request_finish_picking_params)
        self.assertEqual(picking.state, 'done')
