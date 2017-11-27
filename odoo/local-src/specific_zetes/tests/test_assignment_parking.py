# -*- coding: utf-8 -*-

from .. import constants
from .zetes_test_classes import ZetesParkingTest, DEFAULT_HEADER
from ..tools.domain_interface import Parameters
from ..tools.domain_assignment import Assignment

OPERATOR_CODE = '99'


class TestAssignemnt(ZetesParkingTest):
    post_install = True
    at_install = False

    def test_requ_assignment(self):
        # Check with no current picking
        domain = Assignment(DEFAULT_HEADER, request_overwrite=self)
        request_params = Parameters(domain, action='requ')
        request_params.update({
            'Cri01': self.picking_zone_medoc.code,
            'Cri02': None,
            'assignmentType': constants.PARKING_ASSIGNMENT,
            'requestType': '1',
        })

        # Search for a picking
        result_str = domain.requ(request_params)
        result = self.format_result(result_str)
        self.assertEqual(result.respCode, str(constants.RESPONSE_CODE_OK))
        self.assertEqual(result.Usf09, '1')  # Nbr of lines

    def test_01_requ_assignment(self):
        # Check with no current picking
        domain = Assignment(DEFAULT_HEADER, request_overwrite=self)
        request_params = Parameters(domain, action='requ')
        request_params.update({
            'Cri01': self.picking_zone_medoc.code,
            'Cri02': None,
            'assignmentType': constants.PARKING_ASSIGNMENT,
            'requestType': '1',
        })

        # Search for a picking
        result_str = domain.requ(request_params)
        result = self.format_result(result_str)
        self.assertEqual(result.respCode, str(constants.RESPONSE_CODE_OK))
        self.assertEqual(result.Usf09, '1')  # Nbr of lines
