# -*- coding: utf-8 -*-
import mock

from .. import constants
from ..tools.domain_assignment import Assignment
from ..tools.domain_catchweight import Catchweight
from ..tools.domain_interface import Parameters
from .zetes_test_classes import ROUND_CODE, ZetesTest


class TestAssignemnt(ZetesTest):
    def test_requ_assignment(self):
        # Check with no current picking
        domain = Assignment(self._default_header(), mock.MagicMock(name="Savepoint()"))
        request_params = Parameters(domain, action="requ")
        request_params.update(
            {
                "Cri01": None,
                "Cri02": None,
                "assignmentType": constants.PICKING_ASSIGNMENT,
                "requestType": "1",
            }
        )

        self.partner.write({"is_passport_required": True})
        self.picking.picking_type_id.passport = True

        self.assertEqual(
            self.picking.picking_type_id.zetes_picking_type,
            constants.PICKING_ASSIGNMENT,
        )

        # Search for a picking
        result_str = domain.requ(request_params)
        result = self.format_result(result_str)
        self.assertEqual(result.respCode, str(constants.RESPONSE_CODE_OK))
        self.assertEqual(result.groupNum, str(self.picking.id))
        self.assertEqual(result.Usf03, str(ROUND_CODE))  # Round code
        self.assertEqual(result.Usf06, "C")
        self.assertEqual(result.Usf09, "1")  # Nbr of lines

        # Check if the picking has been assigned to the current user
        self.assertEqual(self.picking.operator_id.id, self.operator_user.id)

        # Try with different parameters
        # Set a picking zone (Cri01)
        picking_zone_drugs = self.picking_type_medoc
        request_params.Cri01 = picking_zone_drugs.picking_zone_id.code
        result_str = domain.requ(request_params)
        result = self.format_result(result_str)
        self.assertEqual(result.groupNum, str(self.picking.id))

        # Search for a picking with an operator
        self.picking.operator_id = self.operator_user.id
        result_str = domain.requ(request_params)
        result = self.format_result(result_str)
        self.assertEqual(result.groupNum, str(self.picking.id))

        # Change the state of the round to pending
        self.round.write({"state": "pending"})
        result_str = domain.requ(request_params)
        result = self.format_result(result_str)
        self.assertEqual(result.groupNum, str(self.picking.id))

        # Inventory desactivated
        # # Try to create an inventory for the product 1
        # # This picking should be not available
        # inventory = self.env['stock.inventory'].create({
        #     'name': 'Test',
        #     'filter': 'partial',
        # })
        # inventory.line_ids.create({
        #     'inventory_id': inventory.id,
        #     'product_id': self.product_1.id,
        #     'product_qty': 20,
        #     'location_id': self.env.ref('stock.stock_location_stock').id
        # })
        # # Start the inventory
        # inventory.action_start()
        # result_str = domain.requ(request_params)
        # result = self.format_result(result_str)
        # self.assertEqual(result.respCode, str(constants.RESPONSE_CODE_ERROR))

        # # Now validate the inventory
        # inventory.action_done()
        # result_str = domain.requ(request_params)
        # result = self.format_result(result_str)
        # self.assertEqual(result.respCode, str(constants.RESPONSE_CODE_OK))
        # self.assertEqual(result.groupNum, str(self.picking.id))

    def test_resu_assignement(self):
        self.assertFalse(self.picking.operator_id)

        domain = Assignment(self._default_header(), mock.MagicMock(name="Savepoint()"))
        request_params = Parameters(domain, action="resu")
        # Assign and start the picking
        request_params.update(
            {"groupNum": self.picking.id, "assignmentStatus": constants.AS_START}
        )

        domain.resu(request_params)

        # Do the picking and set the state to done
        request_params.update({"assignmentStatus": constants.AS_DONE, "Usf01": "1"})

        pack_op = self.picking.pack_operation_product_ids[0]
        pack_op.pack_lot_ids.write({"qty": 10})
        pack_op.write({"qty_done": 10})
        domain.resu(request_params)
        self.assertEqual(self.picking.state, "done")

        # Interrupt the picking (NOT cancel the picking himselft)
        request_params.assignmentStatus = constants.AS_CANCELED
        domain.resu(request_params)
        self.assertFalse(self.picking.operator_id)
        self.assertIsNotNone(self.picking.checksum)

    def test_resu_assignment_pack_op_error(self):
        """
        Check that a picking is not validated on resu_assignment if
        a resu_catchweight failed due to a deleted pack operation id
        """
        assignment_domain = Assignment(
            self._default_header(), mock.MagicMock(name="Savepoint()")
        )
        resu_assignment_params = Parameters(assignment_domain, action="resu")
        # Assign and start the picking
        resu_assignment_params.update(
            {"groupNum": self.picking.id, "assignmentStatus": constants.AS_START}
        )

        assignment_domain.resu(resu_assignment_params)

        # unlink and execute pack operation
        pack_op = self.picking.pack_operation_product_ids
        pack_op.ensure_one()
        pack_op_id = pack_op.id
        pack_op.unlink()
        catchweight_domain = Catchweight(
            self._default_header(), mock.MagicMock(name="Savepoint()")
        )
        resu_catchweight_params = Parameters(catchweight_domain, action="resu")
        resu_catchweight_params.update(
            {"lineId": pack_op_id, "Usf01": None, "Usf02": 5, "Usf03": None}
        )
        catchweight_domain.resu(resu_catchweight_params)

        # Finalize the picking (set the state to done)
        resu_assignment_params.update(
            {"assignmentStatus": constants.AS_DONE, "Usf01": "1"}
        )
        assignment_domain.resu(resu_assignment_params)

        # the picking should not be done
        self.assertNotEqual(self.picking.state, "done")
        self.assertTrue(self.picking.zetes_logger_requires_check)

        # if we check the zetes loggers and validate the picking again
        # the picking wil be done
        self.picking.zetes_logger_ids.button_checked()
        self.picking.validate_picking()
        self.assertEqual(self.picking.state, "done")
