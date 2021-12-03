# -*- coding: utf-8 -*-
import mock

from .. import constants
from ..tools.domain_assignment import Assignment
from ..tools.domain_catchweight import Catchweight
from ..tools.domain_interface import Parameters
from ..tools.domain_itemmove import Itemmove
from ..tools.domain_refdata import Refdata
from ..tools.domain_usercontext import Usercontext
from .zetes_test_classes import ZetesReserveTest


class TestFullReserve(ZetesReserveTest):
    def setUp(self):
        self.disable_picking_validation = True
        super(TestFullReserve, self).setUp()

        self.location_product_2 = self.env["stock.location"].create(
            {
                "name": "GD80B2",
                "kind": "bin",
                "zone": "G",
                "corridor": "D",
                "shelf": "80",
                "height": "B",
                "box": "2",
                "location_id": self.zone_gustave.id,
                "bin_checksum_1": "45",
                "bin_checksum_2": "45",
            }
        )
        self.env["stock.location"]._parent_store_compute()

        # Product 2
        # Location: GAD515
        self.product_2 = self.env["product.product"].create(
            {
                "name": "Test medoc 2",
                "default_code": "587502",
                "categ_id": self.product_categ_medoc.id,
                "tracking": "none",
                "list_price": 5,
                "stock_bin_ids": [
                    (
                        0,
                        0,
                        {
                            "sequence": 1,
                            "location_id": self.stock_location.id,
                            "bin_location_id": self.location_product_2.id,
                        },
                    )
                ],
            }
        )

        # Set a quantity in the reserve
        update_qty_wizard = self.env["stock.change.product.qty"].create(
            {
                "product_id": self.product_2.id,
                "product_tmpl_id": self.product_2.product_tmpl_id.id,
                "new_quantity": 100,
                "location_id": self.reserve_medoc.id,
            }
        )
        update_qty_wizard.change_product_qty()

    def test_full(self):
        assignement_obj = Assignment(
            self._default_header(), mock.MagicMock(name="Savepoint()")
        )
        catchweight_obj = Catchweight(
            self._default_header(), mock.MagicMock(name="Savepoint()")
        )
        itemmove_obj = Itemmove(
            self._default_header(), mock.MagicMock(name="Savepoint()")
        )
        refdata_obj = Refdata(
            self._default_header(), mock.MagicMock(name="Savepoint()")
        )
        usercontext_obj = Usercontext(
            self._default_header(), mock.MagicMock(name="Savepoint()")
        )

        ##########
        # Step 1 #
        ##########
        login_params = Parameters(usercontext_obj)
        login_params.update({"contextType": "1"})  # Do a sign in
        result_str = usercontext_obj.requ(login_params)
        result = self.format_result(result_str)
        self.assertEqual(result.respCode, str(constants.RESPONSE_CODE_OK))

        ##########
        # Step 2 #
        ##########
        refdata_params = Parameters(refdata_obj)
        result_str = refdata_obj.requ(refdata_params)
        result_lines = result_str.split("\n")
        results = [self.format_result(result_line) for result_line in result_lines]
        picking_codes = [result_picking.operValue for result_picking in results]
        medic_picking_type = self.picking_type_medoc
        medic_picking_code = medic_picking_type.picking_zone_id.code
        self.assertIn(medic_picking_code, picking_codes)

        ##########
        # Step 3 #
        ##########
        model_name = "report.stock.refill.reassort"
        report = self.env[model_name].search(
            [("product_id", "=", self.product_1.id)], limit=1
        )
        self.assertTrue(len(report))

        picking = report.create_picking()
        self.assertEqual(len(picking.pack_operation_product_ids), 1)
        pack_op = picking.pack_operation_product_ids

        request_picking_params = Parameters(assignement_obj)
        request_picking_params.update(
            {
                "assignmentType": constants.REASSORT_ASSIGNMENT,
                "requestType": "1",
                "tripCounter": "1",
                "Cri01": medic_picking_code,
                "Cri02": None,
            }
        )
        result_str = assignement_obj.requ(request_picking_params)
        result = self.format_result(result_str)
        self.assertEqual(result.respCode, str(constants.RESPONSE_CODE_OK))

        self.assertEqual(result.groupNum, str(picking.id))
        self.assertEqual(result.Usf09, "1")

        start_picking_params = Parameters(assignement_obj)
        start_picking_params.update(
            {"groupNum": picking.id, "assignmentStatus": constants.AS_START}
        )
        assignement_obj.resu(start_picking_params)
        self.assertEqual(picking.operator_id.id, self.operator_user.id)

        ##########
        # Step 4 #
        ##########
        itemmove_params = Parameters(itemmove_obj)
        itemmove_params.update(
            {
                "groupNum": picking.id,
                "itemMoveType": constants.MOVE_TYPE_PUT,
                "Cri01": "0",
            }
        )
        result_str = itemmove_obj.requ(itemmove_params)
        result_lines = result_str.split("\n")
        results = [self.format_result(result_line) for result_line in result_lines]
        self.assertEqual(len(results), 1)
        line_product_1 = results[0]

        # One line:
        # 20 units of product 1 to move from reserve to stock

        # Test line 1
        self.assertFalse(line_product_1.Usf02)
        self.assertEqual(line_product_1.productCode, self.product_1.default_code)
        self.assertEqual(int(line_product_1.reqQty), 20)
        self.assertEqual(
            line_product_1.moveLineId,
            u"{}_{}".format(pack_op.id, self.lot_product_1.id),
        )

        ##########
        # Step 5 #
        ##########
        validate_pick_items_params = Parameters(catchweight_obj)
        validate_pick_items_params.update(
            {
                "groupNum": picking.id,
                "lineId": line_product_1.moveLineId,
                "Usf01": self.lot_product_1.voice_identifier,
                "Usf02": 20,  # Pick 20 items
                "Usf03": None,
            }
        )

        catchweight_obj.resu(validate_pick_items_params)
        self.assertEqual(pack_op.qty_done, 20)

        request_validate_picking_line_request = Parameters(itemmove_obj)
        request_validate_picking_line_request.update(
            {
                "groupNum": picking.id,
                "moveLineId": line_product_1.moveLineId,
                "moveStatus": constants.MOVE_FULL,
                "itemMoveType": constants.MOVE_TYPE_PUT,
            }
        )

        itemmove_obj.resu(request_validate_picking_line_request)
        self.assertEqual(pack_op.zetes_state, constants.MOVE_FULL)
        self.assertEqual(picking.state, "done")

        ##########
        # Step 6 #
        ##########
        model_name = "report.stock.refill.reassort"
        report = self.env[model_name].search(
            [("product_id", "=", self.product_2.id)], limit=1
        )
        self.assertTrue(len(report))

        picking_2 = report.create_picking()
        self.assertEqual(len(picking.pack_operation_product_ids), 1)

        request_picking_params = Parameters(assignement_obj)
        request_picking_params.update(
            {
                "assignmentType": constants.REASSORT_ASSIGNMENT,
                "requestType": "1",
                "tripCounter": "1",
                "Cri01": medic_picking_code,
                "Cri02": None,
            }
        )
        result_str = assignement_obj.requ(request_picking_params)
        result = self.format_result(result_str)
        self.assertEqual(result.respCode, str(constants.RESPONSE_CODE_OK))
        self.assertEqual(result.Usf09, "1")

        pack_op_picking_2 = picking_2.pack_operation_product_ids

        start_picking_params = Parameters(assignement_obj)
        start_picking_params.update(
            {"groupNum": picking_2.id, "assignmentStatus": constants.AS_START}
        )
        assignement_obj.resu(start_picking_params)
        self.assertEqual(picking_2.operator_id.id, self.operator_user.id)

        ##########
        # Step 7 #
        ##########
        itemmove_params = Parameters(itemmove_obj)
        itemmove_params.update(
            {
                "groupNum": picking_2.id,
                "itemMoveType": constants.MOVE_TYPE_PUT,
                "Cri01": "0",
            }
        )
        result_str = itemmove_obj.requ(itemmove_params)
        result_lines = result_str.split("\n")
        results = [self.format_result(result_line) for result_line in result_lines]
        self.assertEqual(len(results), 1)
        line_product_1 = results[0]

        # One line:
        # 100 units of product 2 to move from reserve to stock

        # Test line 1
        self.assertFalse(line_product_1.Usf02)
        self.assertEqual(line_product_1.productCode, self.product_2.default_code)
        self.assertEqual(int(line_product_1.reqQty), 100)
        self.assertTrue(int(line_product_1.moveLineId))

        ##########
        # Step 8 #
        ##########
        validate_pick_items_params = Parameters(catchweight_obj)
        validate_pick_items_params.update(
            {
                "groupNum": picking_2.id,
                "lineId": line_product_1.moveLineId,
                "Usf01": None,
                "Usf02": 80,  # Pick 80 items
                "Usf03": None,
            }
        )

        catchweight_obj.resu(validate_pick_items_params)
        self.assertEqual(len(picking_2.pack_operation_product_ids), 2)
        self.assertEqual(pack_op_picking_2.qty_done, 80)
        pack_op_2_picking_2 = picking_2.pack_operation_product_ids.filtered(
            lambda line: line.qty_done == 20
        )
        self.assertEqual(len(pack_op_2_picking_2), 1)
        self.assertEqual(pack_op_2_picking_2.qty_done, 20)
        self.assertEqual(pack_op_2_picking_2.product_qty, 20)
        self.assertEqual(
            pack_op_2_picking_2.location_id.id, pack_op_2_picking_2.location_dest_id.id
        )

        request_validate_picking_line_request = Parameters(itemmove_obj)
        request_validate_picking_line_request.update(
            {
                "groupNum": picking_2.id,
                "moveLineId": line_product_1.moveLineId,
                "moveStatus": constants.MOVE_FULL,
                "itemMoveType": constants.MOVE_TYPE_PUT,
            }
        )

        itemmove_obj.resu(request_validate_picking_line_request)
        self.assertEqual(pack_op_picking_2.zetes_state, constants.MOVE_FULL)
        self.assertEqual(picking_2.state, "done")
