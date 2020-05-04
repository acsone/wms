# -*- coding: utf-8 -*-
import mock

from .. import constants
from ..tools.domain_interface import Parameters
from ..tools.domain_refdata import Refdata
from .zetes_test_classes import ZetesTest


class TestRefdata(ZetesTest):
    def test_requ_refdata(self):
        """
        :return:
        """
        domain = Refdata(self._default_header(), mock.MagicMock(name="Savepoint()"))
        request_params = Parameters(domain, action="requ")

        result_str = domain.requ(request_params)
        result_lines = result_str.split("\n")

        picking_types = self.env["stock.picking.type"].search(
            [("subcode", "=", "PICK"), ("picking_zone_id", "!=", False)]
        )
        picking_codes = [pick_type.picking_zone_id.code for pick_type in picking_types]

        results = []
        for result_line in result_lines:
            result = self.format_result(result_line)
            results.append(result)
            self.assertEqual(result.respCode, str(constants.RESPONSE_CODE_OK))
            self.assertIn(result.operValue, picking_codes)

        self.assertEqual(len(results), len(picking_types))
