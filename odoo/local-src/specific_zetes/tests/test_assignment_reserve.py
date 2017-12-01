# -*- coding: utf-8 -*-

from .. import constants
from .zetes_test_classes import ZetesReserveTest, DEFAULT_HEADER
from ..tools.domain_interface import Parameters
from ..tools.domain_assignment import Assignment

OPERATOR_CODE = '99'


class TestAssignemnt(ZetesReserveTest):
    post_install = True
    at_install = False

    def test_01_requ_assignment(self):
        # Check with no current picking
        domain = Assignment(DEFAULT_HEADER, request_overwrite=self)
        request_params = Parameters(domain, action='requ')
        request_params.update({
            'Cri01': self.picking_zone_medoc.code,
            'Cri02': None,
            'assignmentType': constants.RESERVE_ASSIGNMENT,
            'requestType': '1',
        })

        # Search for a picking
        result_str = domain.requ(request_params)
        result = self.format_result(result_str)
        self.assertEqual(result.respCode, str(constants.RESPONSE_CODE_OK))
        self.assertEqual(result.Usf09, '1')  # Nbr of lines

    def test_02_requ_assignment(self):
        report_query = """
        SELECT report.id
        FROM report_stock_quant_bylocation_reserve AS report
          LEFT JOIN stock_location ON stock_location.id = report.location_id
          LEFT JOIN picking_zone
            ON stock_location.picking_zone_id = picking_zone.id
        WHERE report.product_id = %s
          AND picking_zone.code = %s
        ORDER BY report.refill_priority
        LIMIT 1
        """
        self.env.cr.execute(report_query, (self.product_1.id,
                                           self.picking_zone_medoc.code))
        result = self.env.cr.fetchone()

        self.assertTrue(result)
        report_id = result[0]

        model_name = 'report.stock.quant.bylocation.reserve'
        report = self.env[model_name].browse(report_id)
        # Create the picking
        picking = report.create_reserve_picking()

        self.assertEqual(picking.zetes_picking_type,
                         constants.RESERVE_ASSIGNMENT)

        # Check with no current picking
        domain = Assignment(DEFAULT_HEADER, request_overwrite=self)
        request_params = Parameters(domain, action='requ')
        request_params.update({
            'Cri01': self.picking_zone_medoc.code,
            'Cri02': None,
            'assignmentType': constants.RESERVE_ASSIGNMENT,
            'requestType': '1',
        })

        self.assertEqual(picking.zetes_picking_type,
                         constants.RESERVE_ASSIGNMENT)

        # Search for a picking
        result_str = domain.requ(request_params)
        result = self.format_result(result_str)
        self.assertEqual(result.respCode, str(constants.RESPONSE_CODE_OK))
        self.assertEqual(result.Usf09, '1')  # Nbr of lines
        self.assertEqual(result.groupNum, str(picking.id))
