# -*- coding: utf-8 -*-
from datetime import datetime

from dateutil.relativedelta import relativedelta

import mock
from odoo import fields
from odoo.tools import mute_logger

from .. import constants
from ..tools.domain_assignment import Assignment
from ..tools.domain_catchweight import Catchweight
from ..tools.domain_interface import Parameters
from ..tools.domain_itempick import Itempick
from ..tools.domain_location import Location
from ..tools.domain_print import Print
from ..tools.domain_refdata import Refdata
from ..tools.domain_usercontext import Usercontext
from .zetes_test_classes import ZetesTest


class TestFull(ZetesTest):
    def setUp(self):
        self.disable_picking_validation = True
        super(TestFull, self).setUp()

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
        # Location: GD80B1
        # Specificity: 10 in stock. 6 taken
        self.product_2 = self.env["product.product"].create(
            {
                "name": "Test medoc 2",
                "default_code": "587502",
                "categ_id": self.product_categ_medoc.id,
                "tracking": "lot",
                "list_price": 40,
                "type": "product",
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

        two_years = datetime.now() + relativedelta(years=2)
        self.lot_product_2 = self.env["stock.production.lot"].create(
            {
                "name": "000000001",
                "product_id": self.product_2.id,
                "removal_date": fields.Datetime.to_string(two_years),
            }
        )
        update_qty_wizard = self.env["stock.change.product.qty"].create(
            {
                "product_id": self.product_2.id,
                "product_tmpl_id": self.product_1.product_tmpl_id.id,
                "new_quantity": 10,
                "lot_id": self.lot_product_2.id,
                "location_id": self.location_product_2.id,
            }
        )
        update_qty_wizard.change_product_qty()

        self.picking.write(
            {
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": "Test medoc 2",
                            "product_id": self.product_2.id,
                            "product_uom_qty": 10,
                            "product_uom": self.env.ref("product.product_uom_unit").id,
                            "location_id": self.env.ref(
                                "stock.stock_location_stock"
                            ).id,
                            "location_dest_id": self.env.ref(
                                "stock.stock_location_output"
                            ).id,
                            "picking_type_id": self.picking_type_medoc.id,
                        },
                    )
                ]
            }
        )

        self.location_product_3 = self.env["stock.location"].create(
            {
                "name": "GD80E8",
                "kind": "bin",
                "zone": "G",
                "corridor": "D",
                "shelf": "80",
                "height": "E",
                "box": "8",
                "location_id": self.zone_gustave.id,
                "bin_checksum_1": "89",
                "bin_checksum_2": "89",
            }
        )
        self.env["stock.location"]._parent_store_compute()

        # Product 3
        # Location: GD80E8
        # Specificity: Split in two lot (20 in lot 000000001
        # and 100 in lot 000000002)
        self.product_3 = self.env["product.product"].create(
            {
                "name": "Test medoc 3",
                "default_code": "025784",
                "categ_id": self.product_categ_medoc.id,
                "tracking": "lot",
                "list_price": 150,
                "type": "product",
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

        two_months = datetime.now() + relativedelta(months=2)
        self.lot_product_3_1 = self.env["stock.production.lot"].create(
            {
                "name": "000000001",
                "product_id": self.product_3.id,
                "removal_date": fields.Datetime.to_string(two_months),
            }
        )
        update_qty_wizard = self.env["stock.change.product.qty"].create(
            {
                "product_id": self.product_3.id,
                "product_tmpl_id": self.product_1.product_tmpl_id.id,
                "new_quantity": 20,
                "lot_id": self.lot_product_3_1.id,
                "location_id": self.location_product_3.id,
            }
        )
        update_qty_wizard.change_product_qty()

        three_months = datetime.now() + relativedelta(months=3)
        self.lot_product_3_2 = self.env["stock.production.lot"].create(
            {
                "name": "000000002",
                "product_id": self.product_3.id,
                "removal_date": fields.Datetime.to_string(three_months),
            }
        )
        update_qty_wizard = self.env["stock.change.product.qty"].create(
            {
                "product_id": self.product_3.id,
                "product_tmpl_id": self.product_1.product_tmpl_id.id,
                "new_quantity": 100,
                "lot_id": self.lot_product_3_2.id,
                "location_id": self.location_product_3.id,
            }
        )
        update_qty_wizard.change_product_qty()

        self.picking.write(
            {
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": "Test medoc 3",
                            "product_id": self.product_3.id,
                            "product_uom_qty": 50,
                            "product_uom": self.env.ref("product.product_uom_unit").id,
                            "location_id": self.env.ref(
                                "stock.stock_location_stock"
                            ).id,
                            "location_dest_id": self.env.ref(
                                "stock.stock_location_output"
                            ).id,
                            "picking_type_id": self.picking_type_medoc.id,
                        },
                    )
                ]
            }
        )

        self.picking.action_assign()
        # Round to the picking
        self.round.button_update()

        logger = self.env["zetes.logger"]
        logger.search([]).unlink()

        printer = self.env["printing.printer"]
        printer.search([]).write({"code": None, "type": None})

        printer_server = self.env["printing.server"].create(
            {"name": "Localhost", "address": "no_printing", "port": "1234"}
        )

        printer.create(
            {
                "name": "Toshiba printer",
                "system_name": "toshiba_printer",
                "code": "20",
                "type": "toshiba",
                "server_id": printer_server.id,
            }
        )

        printer.create(
            {
                "name": "Zebra printer",
                "system_name": "zebra_printer",
                "code": "20",
                "type": "zebra",
                "server_id": printer_server.id,
            }
        )

    @mute_logger(
        "odoo.addons.base_report_to_printer.models.printing_server",
        "odoo.addons.specific_zetes.tools.domain_print",
        "odoo.addons.specific_print.models.stock",
    )
    def test_full(self):
        """
        Please read the README file to understand the test
        :return:
        """
        assignement_obj = Assignment(
            self._default_header(), mock.MagicMock(name="Savepoint()")
        )
        catchweight_obj = Catchweight(
            self._default_header(), mock.MagicMock(name="Savepoint()")
        )
        itempick_obj = Itempick(
            self._default_header(), mock.MagicMock(name="Savepoint()")
        )
        location_obj = Location(
            self._default_header(), mock.MagicMock(name="Savepoint()")
        )
        print_obj = Print(self._default_header(), mock.MagicMock(name="Savepoint()"))
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
        request_picking_params = Parameters(assignement_obj)
        request_picking_params.update(
            {
                "assignmentType": constants.PICKING_ASSIGNMENT,
                "requestType": "1",
                "tripCounter": "1",
                "Cri01": medic_picking_code,
                "Cri02": None,
            }
        )
        result_str = assignement_obj.requ(request_picking_params)
        result = self.format_result(result_str)
        self.assertEqual(result.respCode, str(constants.RESPONSE_CODE_OK))
        self.assertEqual(result.groupNum, str(self.picking.id))
        self.assertEqual(result.Usf06, "E")
        self.assertEqual(result.assignmentStatus, str(constants.AS_DEFAULT))

        start_picking_params = Parameters(assignement_obj)
        start_picking_params.update(
            {"groupNum": self.picking.id, "assignmentStatus": constants.AS_START}
        )
        assignement_obj.resu(start_picking_params)
        self.assertEqual(self.picking.operator_id.id, self.operator_user.id)

        ##########
        # Step 4 #
        ##########
        request_picking_lines_params = Parameters(itempick_obj)
        request_picking_lines_params.update(
            {
                "groupNum": self.picking.id,
                "tripCounter": "1",
                "Cri01": "0",
                "Usf06": None,
            }
        )
        result_str = itempick_obj.requ(request_picking_lines_params)
        result_lines = result_str.split("\n")
        results = [self.format_result(result_line) for result_line in result_lines]
        self.assertEqual(len(results), 4)
        line_product_1 = results[0]
        line_product_2 = results[1]
        line_product_3_lot_1 = results[2]
        line_product_3_lot_2 = results[3]

        pack_operations = self.env["stock.pack.operation"].search(
            [("picking_id", "=", self.picking.id)], order="location_name ASC, id"
        )
        self.assertEqual(len(pack_operations), 3)

        # Test line 1
        pack_op_1 = pack_operations[0]
        pack_op_1_id, lot_id = line_product_1.pickLineId.split("_")
        self.assertEqual(pack_op_1_id, str(pack_op_1.id))
        self.assertEqual(lot_id, str(self.lot_product_1.id))
        self.assertEqual(line_product_1.productCode, self.product_1.default_code)
        self.assertEqual(int(line_product_1.reqQty), 10)
        # Check the location only for the first line.
        # It's not useful to test on each line
        self.assertEqual(line_product_1.sourceLC1, "G")
        self.assertEqual(line_product_1.sourceLC2, "D")
        self.assertEqual(line_product_1.sourceLC3, "80")
        self.assertEqual(line_product_1.sourceLC4, "B")
        self.assertEqual(line_product_1.sourceLC5, "1")
        self.assertEqual(line_product_1.sourceLCCD, "12")
        self.assertEqual(line_product_1.Usf01, self.lot_product_1.voice_identifier)

        # Test line 2
        pack_op_2 = pack_operations[1]
        pack_op_2_id, lot_id = line_product_2.pickLineId.split("_")
        self.assertEqual(pack_op_2_id, str(pack_op_2.id))
        self.assertEqual(lot_id, str(self.lot_product_2.id))
        self.assertEqual(line_product_2.productCode, self.product_2.default_code)
        self.assertEqual(int(line_product_2.reqQty), 10)
        self.assertEqual(line_product_2.Usf01, self.lot_product_2.voice_identifier)

        # Test line 3
        pack_op_3 = pack_operations[2]
        pack_op_id, lot_id, = line_product_3_lot_1.pickLineId.split("_")
        self.assertEqual(pack_op_id, str(pack_op_3.id))
        self.assertEqual(lot_id, str(self.lot_product_3_1.id))
        self.assertEqual(line_product_3_lot_1.productCode, self.product_3.default_code)
        self.assertEqual(int(line_product_3_lot_1.reqQty), 20)
        self.assertEqual(
            line_product_3_lot_1.Usf01, self.lot_product_3_1.voice_identifier
        )
        self.assertEqual(line_product_3_lot_1.Usf02, self.lot_product_3_1.checksum)

        # Test line 4
        pack_op_3 = pack_operations[2]
        pack_op_id, lot_id, = line_product_3_lot_2.pickLineId.split("_")
        self.assertEqual(pack_op_id, str(pack_op_3.id))
        self.assertEqual(lot_id, str(self.lot_product_3_2.id))
        self.assertEqual(line_product_3_lot_2.productCode, self.product_3.default_code)
        self.assertEqual(int(line_product_3_lot_2.reqQty), 30)
        self.assertEqual(
            line_product_3_lot_2.Usf01, self.lot_product_3_2.voice_identifier
        )
        self.assertEqual(line_product_3_lot_2.Usf02, self.lot_product_3_2.checksum)

        ##########
        # Step 5 #
        ##########
        request_catchweight_params = Parameters(catchweight_obj)
        request_catchweight_params.update(
            {
                "groupNum": self.picking.id,
                "pickLineId": pack_op_1.id,
                "productCode": self.product_1.default_code,
                "lotNumber": self.lot_product_1.voice_identifier,
                "effQty": None,
            }
        )

        result_str = catchweight_obj.requ(request_catchweight_params)
        result = self.format_result(result_str)

        self.assertEqual(result.respCode, str(constants.RESPONSE_CODE_OK))

        request_pick_items_params = Parameters(catchweight_obj)
        request_pick_items_params.update(
            {
                "groupNum": self.picking.id,
                "lineId": pack_op_1.id,
                "Usf01": self.lot_product_1.voice_identifier,
                "Usf02": 10,  # Pick 10 items
                "Usf03": None,
            }
        )

        catchweight_obj.resu(request_pick_items_params)
        self.assertEqual(pack_op_1.qty_done, 10)

        ##########
        # Step 6 #
        ##########
        request_validate_picking_line_request = Parameters(itempick_obj)
        request_validate_picking_line_request.update(
            {
                "groupNum": self.picking.id,
                "pickLineId": pack_op_1.id,
                "pickStatus": constants.OP_PICKED,
            }
        )

        itempick_obj.resu(request_validate_picking_line_request)
        self.assertEqual(pack_op_1.zetes_state, constants.OP_PICKED)

        ##########
        # Step 7 #
        ##########
        request_catchweight_params = Parameters(catchweight_obj)
        request_catchweight_params.update(
            {
                "groupNum": self.picking.id,
                "pickLineId": pack_op_2.id,
                "productCode": self.product_2.default_code,
                "lotNumber": self.lot_product_2.voice_identifier,
                "effQty": None,
            }
        )

        result_str = catchweight_obj.requ(request_catchweight_params)
        result = self.format_result(result_str)

        self.assertEqual(result.respCode, str(constants.RESPONSE_CODE_OK))

        # Take only 6 items
        request_pick_items_params = Parameters(catchweight_obj)
        request_pick_items_params.update(
            {
                "groupNum": self.picking.id,
                "lineId": pack_op_2.id,
                "Usf01": self.lot_product_2.voice_identifier,
                "Usf02": 6,  # Pick 6 items,
                "Usf03": None,
            }
        )

        catchweight_obj.resu(request_pick_items_params)
        self.assertEqual(pack_op_2.qty_done, 6)

        ##########
        # Step 8 #
        ##########
        request_validate_picking_line_params = Parameters(itempick_obj)
        request_validate_picking_line_params.update(
            {
                "groupNum": self.picking.id,
                "pickLineId": pack_op_2.id,
                "pickStatus": constants.OP_PICKED,
            }
        )

        itempick_obj.resu(request_validate_picking_line_params)
        self.assertEqual(pack_op_2.zetes_state, constants.OP_PICKED)

        ##########
        # Step 9 #
        ##########
        request_catchweight_params = Parameters(catchweight_obj)
        request_catchweight_params.update(
            {
                "groupNum": self.picking.id,
                "pickLineId": pack_op_3.id,
                "productCode": self.product_3.default_code,
                "lotNumber": self.lot_product_3_1.voice_identifier,
                "effQty": None,
            }
        )

        result_str = catchweight_obj.requ(request_catchweight_params)
        result = self.format_result(result_str)

        self.assertEqual(result.respCode, str(constants.RESPONSE_CODE_OK))

        # Take 20 items in the first lot
        request_pick_items_params = Parameters(catchweight_obj)
        request_pick_items_params.update(
            {
                "groupNum": self.picking.id,
                "lineId": pack_op_3.id,
                "Usf01": self.lot_product_3_1.voice_identifier,
                "Usf02": 20,
                "Usf03": None,
            }
        )

        # The lot 20 is empty now. The picker will change the lot
        request_location_params = Parameters(location_obj)
        request_location_params.update(
            {
                "lineId": pack_op_3.id,
                "Cri01": self.location_product_3.zone,
                "Cri02": self.location_product_3.corridor,
                "Cri03": self.location_product_3.shelf,
                "Cri04": self.location_product_3.height,
                "Cri05": self.location_product_3.box,
                "Cri07": self.lot_product_3_2.checksum,
            }
        )

        result_str = location_obj.requ(request_location_params)
        result = self.format_result(result_str)
        self.assertEqual(result.respCode, str(constants.RESPONSE_CODE_OK))
        self.assertEqual(result.Usf01, self.lot_product_3_2.voice_identifier)
        self.assertFalse(result.Usf03)

        catchweight_obj.resu(request_pick_items_params)
        self.assertEqual(pack_op_3.qty_done, 20)

        # Take 30 items in the second lot
        request_pick_items_params = Parameters(catchweight_obj)
        request_pick_items_params.update(
            {
                "groupNum": self.picking.id,
                "lineId": pack_op_3.id,
                "Usf01": self.lot_product_3_2.voice_identifier,
                "Usf02": 30,
                "Usf03": None,
            }
        )

        catchweight_obj.resu(request_pick_items_params)
        self.assertEqual(pack_op_3.qty_done, 50)

        ###########
        # Step 10 #
        ###########
        request_validate_picking_line_params = Parameters(itempick_obj)
        request_validate_picking_line_params.update(
            {
                "groupNum": self.picking.id,
                "pickLineId": pack_op_3.id,
                "pickStatus": constants.OP_PICKED,
            }
        )

        itempick_obj.resu(request_validate_picking_line_params)
        self.assertEqual(pack_op_3.zetes_state, constants.OP_PICKED)

        ###########
        # Step 11 #
        ###########
        request_print_params = Parameters(print_obj)
        request_print_params.update(
            {
                "groupNum": self.picking.id,
                "printType": constants.PRINT_LABELS,
                "printerNum": 20,
                "Usf01": 1,
            }
        )

        result_str = print_obj.requ(request_print_params)
        result = self.format_result(result_str)

        self.assertEqual(result.respCode, str(constants.RESPONSE_CODE_ERROR))
        self.assertEqual(result.labelCD, "00")
        self.assertEqual(result.respMsg, "Error during printing")

        ###########
        # Step 12 #
        ###########
        request_finish_picking_params = Parameters(assignement_obj)
        request_finish_picking_params.update(
            {
                "groupNum": self.picking.id,
                "assignmentStatus": constants.AS_DONE,
                "Usf01": 1,
            }
        )

        with mute_logger("odoo.addons.specific_zetes.tools.domain_assignment"):
            # to make travis happy but not sure if this is an expected
            # behaviour
            assignement_obj.resu(request_finish_picking_params)
        self.assertEqual(self.picking.state, "done")

        ###########
        # Step 13 #
        ###########
        request_picking_params = Parameters(assignement_obj)
        request_picking_params.update(
            {
                "assignmentType": constants.PICKING_ASSIGNMENT,
                "requestType": "1",
                "tripCounter": "1",
                "Cri01": medic_picking_code,
                "Cri02": None,
            }
        )

        result_str = assignement_obj.requ(request_picking_params)
        result = self.format_result(result_str)

        # as per ALCYN-2130, we put the backorder in the delivery round,
        # we assign a delivery round to the backorders, a picking exists
        self.assertEqual(result.respCode, str(constants.RESPONSE_CODE_OK))
