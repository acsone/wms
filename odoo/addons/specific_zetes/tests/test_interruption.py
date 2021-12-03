# -*- coding: utf-8 -*-
from datetime import datetime

import mock
from dateutil.relativedelta import relativedelta

from odoo import fields

from .. import constants
from ..tools.domain_assignment import Assignment
from ..tools.domain_catchweight import Catchweight
from ..tools.domain_interface import Parameters
from ..tools.domain_itempick import Itempick
from ..tools.domain_usercontext import Usercontext
from .zetes_test_classes import ZetesTest


class TestInterruption(ZetesTest):
    def setUp(self):
        self.disable_picking_validation = True
        super(TestInterruption, self).setUp()

        self.operator_user_2 = self.env["res.users"].create(
            {
                "name": "User test 2",
                "ref": "947356253648689",
                "login": "zetes_user_test_2",
                "operator_code": "98",
                "groups_id": [(4, self.env.ref("stock.group_stock_user").id)],
                "tz": "Europe/Brussels",
                "lang": "en_US",
                "email": "hello2@world.com",
            }
        )

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
                        },
                    )
                ]
            }
        )

        self.picking.action_assign()
        # Round to the picking
        self.round.with_context(test_queue_job_no_delay=True).button_update()

        printer = self.env["printing.printer"]
        printer.search([]).unlink()

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
                "name": "Passport printer",
                "system_name": "zebra_printer",
                "code": "1",
                "type": "pdf",
                "server_id": printer_server.id,
            }
        )

    def test_interruption(self):
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
        usercontext_obj = Usercontext(
            self._default_header(), mock.MagicMock(name="Savepoint()")
        )

        ##########
        # Step 1 #
        ##########
        # Start the picking
        start_picking_params = Parameters(assignement_obj)
        start_picking_params.update(
            {"groupNum": self.picking.id, "assignmentStatus": constants.AS_START}
        )
        assignement_obj.resu(start_picking_params)

        pack_op_1 = self.picking.pack_operation_product_ids[0]
        pack_op_2 = self.picking.pack_operation_product_ids[1]

        ##########
        # Step 2 #
        ##########
        # Pick 10 items for the first move
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

        request_validate_picking_line_params = Parameters(itempick_obj)
        request_validate_picking_line_params.update(
            {
                "groupNum": self.picking.id,
                "pickLineId": pack_op_1.id,
                "pickStatus": constants.OP_PICKED,
            }
        )
        itempick_obj.resu(request_validate_picking_line_params)

        ##########
        # Step 3 #
        ##########
        request_interruption_params = Parameters(assignement_obj)
        request_interruption_params.update(
            {"groupNum": self.picking.id, "assignmentStatus": constants.AS_CANCELED}
        )
        assignement_obj.resu(request_interruption_params)

        ##########
        # Step 4 #
        ##########
        user_2_header = list(self._default_header())
        user_2_header[constants.USER_INDEX] = self.operator_user_2.operator_code

        new_usercontext_obj = Usercontext(
            user_2_header, mock.MagicMock(name="Savepoint()")
        )
        new_assignment_obj = Assignment(
            user_2_header, mock.MagicMock(name="Savepoint()")
        )
        new_itempick_obj = Itempick(user_2_header, mock.MagicMock(name="Savepoint()"))

        request_usercontext_params = Parameters(new_usercontext_obj)
        request_usercontext_params.update({"contextType": "1"})  # Do a sign in
        result_str = usercontext_obj.requ(request_usercontext_params)
        result = self.format_result(result_str)
        self.assertEqual(result.unitSlam, "0")

        medic_picking_type = self.picking_type_medoc
        medic_picking_code = medic_picking_type.picking_zone_id.code

        request_assignment_params = Parameters(new_assignment_obj)
        request_assignment_params.update(
            {
                "Cri02": None,
                "Cri01": medic_picking_code,
                "assignmentType": constants.PICKING_ASSIGNMENT,
                "requestType": 1,
            }
        )
        result_str = assignement_obj.requ(request_assignment_params)
        result = self.format_result(result_str)
        self.assertEqual(result.respCode, str(constants.RESPONSE_CODE_OK))
        self.assertEqual(result.groupNum, str(self.picking.id))

        request_picking_lines_params = Parameters(new_itempick_obj)
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
        self.assertEqual(len(results), 1)
        pick_line_id, lot_id = results[0].pickLineId.split("_")
        self.assertEqual(pick_line_id, str(pack_op_2.id))
        self.assertEqual(lot_id, str(self.lot_product_2.id))
