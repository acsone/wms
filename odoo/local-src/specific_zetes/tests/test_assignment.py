# -*- coding: utf-8 -*-
from .. import constants
from .zetes_test_classes import ZetesTest, DEFAULT_HEADER, \
    ROUND_CODE, PARTNER_NAME
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
            'requestType': '1',
        })

        self.partner.write({
            'is_passport_required': True,
        })

        # Search for a picking
        result_str = domain.requ(request_params)
        result = self.format_result(result_str)
        self.assertEqual(result.respCode, str(constants.RESPONSE_CODE_OK))
        self.assertEqual(result.groupNum, str(self.picking.id))
        self.assertEqual(result.Usf03, str(ROUND_CODE))  # Round code
        self.assertEqual(result.Usf06, 'C')
        self.assertEqual(result.Usf07, PARTNER_NAME)  # Name of partner
        self.assertEqual(result.Usf09, '1')  # Nbr of lines

        # Try with different parameters
        # Set a picking zone (Cri01)
        picking_zone_drugs = self.env.ref('__setup__.stock_picking_type_medoc')
        request_params.Cri01 = picking_zone_drugs.zone_code
        result_str = domain.requ(request_params)
        result = self.format_result(result_str)
        self.assertEqual(result.groupNum, str(self.picking.id))

        # Search for a picking with an operator
        request_params.requestType = None
        result_str = domain.requ(request_params)
        result = self.format_result(result_str)
        self.assertEqual(result.respCode, str(constants.RESPONSE_CODE_ERROR))

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

        move = self.picking.pack_operation_product_ids[0]
        move.pack_lot_ids.write({
            'qty': 10,
        })
        move.write({
            'qty_done': 10,
        })
        domain.resu(request_params)
        self.assertEqual(self.picking.state, 'done')

        # Interrupt the picking (NOT cancel the picking himselft)
        request_params.assignmentStatus = constants.AS_CANCELED
        domain.resu(request_params)
        self.assertFalse(self.picking.operator_id)
        self.assertIsNotNone(self.picking.checksum)
