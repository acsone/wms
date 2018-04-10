# -*- coding: utf-8 -*-
from .. import constants
from .zetes_test_classes import ZetesTest, DEFAULT_HEADER, ROUND_CODE
from ..tools.domain_interface import Parameters
from ..tools.domain_assignment import Assignment


class TestAssignemnt(ZetesTest):

    def test_requ_assignment(self):
        # Check with no current picking
        domain = Assignment(DEFAULT_HEADER, request_overwrite=self)
        request_params = Parameters(domain, action='requ')
        request_params.update({
            'Cri01': None,
            'Cri02': None,
            'assignmentType': constants.PICKING_ASSIGNMENT,
            'requestType': '1',
        })

        self.partner.write({
            'is_passport_required': True,
        })

        self.assertEqual(self.picking.zetes_picking_type,
                         constants.PICKING_ASSIGNMENT)

        # Search for a picking
        result_str = domain.requ(request_params)
        result = self.format_result(result_str)
        self.assertEqual(result.respCode, str(constants.RESPONSE_CODE_OK))
        self.assertEqual(result.groupNum, str(self.picking.id))
        self.assertEqual(result.Usf03, str(ROUND_CODE))  # Round code
        self.assertEqual(result.Usf06, 'C')
        self.assertEqual(result.Usf09, '1')  # Nbr of lines

        # Try with different parameters
        # Set a picking zone (Cri01)
        picking_zone_drugs = self.picking_type_medoc
        request_params.Cri01 = picking_zone_drugs.picking_zone_id.code
        result_str = domain.requ(request_params)
        result = self.format_result(result_str)
        self.assertEqual(result.groupNum, str(self.picking.id))

        # Search for a picking with an operator
        self.picking.operator_id = self.user.id
        result_str = domain.requ(request_params)
        result = self.format_result(result_str)
        self.assertEqual(result.groupNum, str(self.picking.id))

    def test_resu_assignement(self):
        self.assertFalse(self.picking.operator_id)

        domain = Assignment(DEFAULT_HEADER, request_overwrite=self)
        request_params = Parameters(domain, action='resu')
        # Assign and start the picking
        request_params.update({
            'groupNum': self.picking.id,
            'assignmentStatus': constants.AS_START,
        })

        domain.resu(request_params)
        self.assertEqual(self.picking.operator_id.id, self.user.id)

        # Do the picking and set the state to done
        request_params.update({
            'assignmentStatus': constants.AS_DONE,
            'Usf01': '1',
        })

        pack_op = self.picking.pack_operation_product_ids[0]
        pack_op.pack_lot_ids.write({
            'qty': 10,
        })
        pack_op.write({
            'qty_done': 10,
        })
        domain.resu(request_params)
        self.assertEqual(self.picking.state, 'done')

        # Interrupt the picking (NOT cancel the picking himselft)
        request_params.assignmentStatus = constants.AS_CANCELED
        domain.resu(request_params)
        self.assertFalse(self.picking.operator_id)
        self.assertIsNotNone(self.picking.checksum)
